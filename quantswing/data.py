"""
Kursdaten laden, prüfen und zwischenspeichern.

Quelle ist Yahoo Finance (über das Paket `yfinance`). Damit sind Aktien
weltweit abrufbar – das Börsenkürzel bestimmt den Handelsplatz:
  AAPL      USA            SAP.DE   Xetra          ASML.AS  Amsterdam
  NESN.SW   Schweiz        7203.T   Tokio          BTC-USD  Krypto
Kurse sind dividenden- und split-bereinigt (auto_adjust=True).
"""

from __future__ import annotations

import logging
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .markets import CRYPTO, asset_class, fx_symbol, market_of  # noqa: F401

log = logging.getLogger(__name__)

OHLCV = ["Open", "High", "Low", "Close", "Volume"]



class DataError(Exception):
    """Daten fehlen oder sind unbrauchbar."""


def clean_ohlcv(df: pd.DataFrame, symbol: str = "?") -> pd.DataFrame:
    """
    Prüft und bereinigt Kursdaten. Fehler werden gemeldet statt verschluckt.

    - entfernt Zeilen ohne Kurs, mit Kurs <= 0 oder mit High < Low
    - repariert Open/Close, die minimal außerhalb von High/Low liegen
    - sortiert nach Datum und entfernt doppelte Tage
    """
    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        raise DataError(f"{symbol}: Spalten fehlen: {missing}")

    df = df[OHLCV].copy()
    df = df[~df.index.duplicated(keep="last")].sort_index()

    before = len(df)
    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    df = df[(df[["Open", "High", "Low", "Close"]] > 0).all(axis=1)]
    df = df[df["High"] >= df["Low"]]
    dropped = before - len(df)
    if dropped:
        log.info("%s: %d fehlerhafte Zeilen entfernt", symbol, dropped)

    df["High"] = df[["High", "Open", "Close"]].max(axis=1)
    df["Low"] = df[["Low", "Open", "Close"]].min(axis=1)
    df["Volume"] = df["Volume"].fillna(0.0)

    # Verdächtige Sprünge (>60 % an einem Tag) bei Aktien deuten auf
    # fehlerhafte Split-Bereinigung hin – nur warnen, nicht löschen.
    if asset_class(symbol) == "stock" and len(df) > 1:
        jumps = df["Close"].pct_change().abs() > 0.6
        if jumps.any():
            log.warning(
                "%s: %d verdächtige Kurssprünge >60%% (z.B. %s) – Daten prüfen",
                symbol, int(jumps.sum()), df.index[jumps][0].date(),
            )
    return df


def _cache_path(cache_dir: str | Path, symbol: str, interval: str, start: str,
                end: str | None) -> Path:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe = symbol.replace("/", "_").replace("^", "IDX_").replace("=", "_")
    stamp = end or f"stand-{date.today().isoformat()}"
    return cache_dir / f"{safe}_{interval}_{start}_{stamp}.csv"


def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
    if isinstance(raw.columns, pd.MultiIndex):
        raw = raw.copy()
        raw.columns = raw.columns.get_level_values(0)
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    return raw


def _yf():
    try:
        import yfinance as yf
    except ImportError as e:  # pragma: no cover
        raise DataError("Paket 'yfinance' fehlt: pip install -r requirements.txt") from e
    return yf


def load_ohlcv(
    symbol: str,
    start: str = "2005-01-01",
    end: str | None = None,
    cache_dir: str | Path | None = ".cache/prices",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Tageskerzen für ein Symbol laden (mit Datei-Cache).
    Ohne `end` gilt der Cache nur für den heutigen Tag, danach wird neu geladen.
    """
    cache_file = _cache_path(cache_dir, symbol, interval, start, end) if cache_dir else None
    if cache_file is not None and cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        if df.empty:
            raise DataError(f"{symbol}: keine Daten (aus Cache)")
        return clean_ohlcv(df, symbol)

    yf = _yf()
    raw, last_err = None, None
    for attempt in range(3):  # Yahoo drosselt gelegentlich – kurz warten, erneut versuchen
        try:
            raw = yf.download(
                symbol, start=start, end=end, interval=interval,
                auto_adjust=True, progress=False, threads=False,
            )
            if raw is not None and not raw.empty:
                break
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(2 * (attempt + 1))
    if raw is None or raw.empty:
        raise DataError(f"{symbol}: keine Daten von Yahoo erhalten ({last_err or 'leer'})")

    df = clean_ohlcv(_normalize(raw), symbol)
    if cache_file is not None:
        df.to_csv(cache_file)
    return df


def prefetch(
    symbols: list[str],
    start: str = "2005-01-01",
    end: str | None = None,
    cache_dir: str | Path = ".cache/prices",
    chunk: int = 40,
    interval: str = "1d",
) -> list[str]:
    """
    Lädt viele Symbole paketweise in den Cache (deutlich schneller und
    schonender für Yahoo als einzeln). Gibt die Symbole zurück, für die
    nichts geladen werden konnte – diese versucht `load_ohlcv` später einzeln.
    """
    todo = [s for s in symbols if not _cache_path(cache_dir, s, interval, start, end).exists()]
    missing: list[str] = []
    if not todo:
        return missing
    yf = _yf()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        try:
            raw = yf.download(
                part, start=start, end=end, interval=interval, group_by="ticker",
                auto_adjust=True, progress=False, threads=True,
            )
        except Exception as e:  # noqa: BLE001
            log.warning("Paket-Download fehlgeschlagen (%s) – einzeln weiter", e)
            missing += part
            continue
        for sym in part:
            try:
                sub = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw
                sub = _normalize(sub.dropna(how="all"))
                if sub.empty:
                    raise DataError("leer")
                clean_ohlcv(sub, sym).to_csv(_cache_path(cache_dir, sym, interval, start, end))
            except Exception:  # noqa: BLE001
                missing.append(sym)
        time.sleep(1.0)
    return missing


def load_fx_usd(currency: str, start: str = "2005-01-01",
                cache_dir: str | Path | None = ".cache/prices") -> pd.Series | None:
    """
    Wechselkurs: Wie viele USD ist 1 Einheit `currency` wert (Tagesschluss)?
    None, wenn kein Kurs verfügbar ist.
    """
    sym = fx_symbol(currency)
    if sym is None:
        return None
    try:
        return load_ohlcv(sym, start=start, cache_dir=cache_dir)["Close"]
    except DataError as e:
        log.warning("Wechselkurs %s nicht verfügbar: %s", currency, e)
        return None


def turnover_usd(df: pd.DataFrame, symbol: str, fx: pd.Series | None = None,
                 window: int = 60) -> pd.Series:
    """
    Gehandelter Wert pro Tag in USD, als Median der letzten `window` Tage
    (nur Vergangenheit, also kein Blick in die Zukunft).

    Ohne passenden Wechselkurs (fx=None bei Nicht-USD-Werten) ist das Ergebnis NaN.
    """
    m = market_of(symbol)
    if m is CRYPTO:
        daily = df["Volume"].astype(float)          # Yahoo liefert Krypto-Volumen bereits in USD
    else:
        daily = df["Close"] / m.price_divisor * df["Volume"]
        if m.currency != "USD":
            if fx is None:
                return pd.Series(np.nan, index=df.index)
            rate = fx.reindex(df.index.union(fx.index)).ffill().reindex(df.index)
            daily = daily * rate
    return daily.rolling(window, min_periods=window // 2).median()


def synthetic_ohlcv(
    n: int = 2500,
    seed: int = 7,
    start: str = "2010-01-01",
    drift: float = 0.0003,
    vol: float = 0.015,
    start_price: float = 100.0,
) -> pd.DataFrame:
    """
    Künstliche Kursdaten (Zufallspfad mit Trendphasen) für Tests und den
    Offline-Demo-Modus. Hat KEINE Aussagekraft über echte Märkte.
    """
    rng = np.random.default_rng(seed)
    regime = np.repeat(rng.choice([-1.0, 0.0, 1.0], size=n // 100 + 1), 100)[:n]
    rets = rng.normal(drift + regime * 0.0008, vol, n)
    close = start_price * np.exp(np.cumsum(rets))
    open_ = np.r_[start_price, close[:-1]] * np.exp(rng.normal(0, vol * 0.3, n))
    spread = np.abs(rng.normal(0, vol * 0.6, n))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    volume = rng.lognormal(13, 0.4, n)
    idx = pd.bdate_range(start, periods=n)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )
