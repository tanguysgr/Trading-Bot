"""
Prüf-Charts: zeigt, was der Bot auf einem Chart "sieht".

Zweck: Bevor eine Strategie getestet wird, soll man mit eigenen Augen prüfen
können, ob Swings, BOS/CHoCH, Fibonacci und Zonen so erkannt werden, wie man
sie selbst (z.B. in TradingView) einzeichnen würde.

Wichtig beim Lesen: Swing-Punkte sind an ihrer eigenen Kerze markiert, der Bot
kennt sie aber erst einige Kerzen später (siehe structure.py).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import indicators as ind  # noqa: E402
from .structure import (  # noqa: E402
    EVENT_LABELS, LONG, SHORT, PivotBook, fib_legs, fib_price, market_structure, pivots, zones_at,
)

UP, DOWN = "#1a9850", "#d73027"
FIB_RATIOS = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)


def _candles(ax, d: pd.DataFrame) -> None:
    x = np.arange(len(d))
    up = d["Close"] >= d["Open"]
    for mask, color in ((up, UP), (~up, DOWN)):
        xs = x[mask.to_numpy()]
        sub = d[mask]
        ax.vlines(xs, sub["Low"], sub["High"], color=color, linewidth=0.7)
        body_lo = np.minimum(sub["Open"], sub["Close"])
        body_h = (sub["Close"] - sub["Open"]).abs().clip(lower=1e-9)
        ax.bar(xs, body_h, bottom=body_lo, width=0.6, color=color, edgecolor=color, linewidth=0.3)


def plot_structure(df: pd.DataFrame, symbol: str, start: str, out: str | Path,
                   swing_len: int = 5) -> Path:
    """Zeichnet Kerzen, SMA 50/200, Swings, BOS/CHoCH, aktive Fibonacci-Schenkel und Zonen."""
    atr = ind.atr(df)
    piv = pivots(df, swing_len, swing_len)
    ms = market_structure(df, piv=piv)
    legs = fib_legs(df, piv, atr)
    sma50, sma200 = ind.sma(df["Close"], 50), ind.sma(df["Close"], 200)

    pos0 = int(np.searchsorted(df.index, pd.Timestamp(start)))
    d = df.iloc[pos0:]
    last = len(df) - 1
    x = lambda pos: pos - pos0  # noqa: E731  (Kerzen-Position -> x-Achse)

    fig, ax = plt.subplots(figsize=(15, 7.5))
    _candles(ax, d)
    ax.plot(np.arange(len(d)), sma50.iloc[pos0:], color="#2c7fb8", lw=1.3, label="SMA 50")
    ax.plot(np.arange(len(d)), sma200.iloc[pos0:], color="#7b3294", lw=1.3, label="SMA 200")

    # Swings (an der Swing-Kerze, bekannt erst später)
    for col, bar_col, marker, color, off in (("PH", "PH_BAR", "v", DOWN, 1.006), ("PL", "PL_BAR", "^", UP, 0.994)):
        ok = piv[col].notna() & (piv[bar_col] >= pos0)
        ax.scatter([x(int(b)) for b in piv.loc[ok, bar_col]], piv.loc[ok, col] * off,
                   marker=marker, color=color, s=28, zorder=5)

    # BOS / CHoCH: Linie vom gebrochenen Swing bis zur Bruch-Kerze
    for t in np.flatnonzero(ms["EVENT"].to_numpy() != 0):
        if t < pos0:
            continue
        e = int(ms["EVENT"].iat[t])
        lvl, b = ((ms["LEVEL_HIGH"].iat[t], ms["LEVEL_HIGH_BAR"].iat[t]) if e > 0
                  else (ms["LEVEL_LOW"].iat[t], ms["LEVEL_LOW_BAR"].iat[t]))
        color = UP if e > 0 else DOWN
        ax.hlines(lvl, x(max(int(b), pos0)), x(t), color=color, lw=1.0,
                  linestyles="-" if abs(e) == 1 else "--")
        ax.annotate(EVENT_LABELS[e], (x(t), lvl), textcoords="offset points",
                    xytext=(3, 4 if e > 0 else -11), fontsize=7.5, color=color, weight="bold")

    # Aktive Fibonacci-Schenkel an der letzten Kerze
    for hi_c, lo_c, direction, color in (("UP_HI", "UP_LO", LONG, UP), ("DN_HI", "DN_LO", SHORT, DOWN)):
        hi, lo = legs[hi_c].iat[last], legs[lo_c].iat[last]
        if np.isnan(hi):
            continue
        x0 = x(last) - 40
        for r in FIB_RATIOS:
            yv = fib_price(hi, lo, r, direction)
            ax.hlines(yv, x0, x(last) + 3, color=color, lw=0.7, alpha=0.7, linestyles=":")
            ax.text(x(last) + 4, yv, f"{r:.3f}", fontsize=7, color=color, va="center")
        z_lo, z_hi = sorted((fib_price(hi, lo, 0.5, direction), fib_price(hi, lo, 0.618, direction)))
        ax.axhspan(z_lo, z_hi, xmin=(x0 - ax.get_xlim()[0]) / max(1, len(d)), color=color, alpha=0.10,
                   label=f"Fibonacci 0,5–0,618 ({'Long' if direction == LONG else 'Short'})")

    # Zonen an der letzten Kerze
    for i, z in enumerate(zones_at(PivotBook(piv), last, atr.iat[last])):
        if z.top < d["Low"].min() or z.bottom > d["High"].max():
            continue
        ax.axhspan(z.bottom, z.top, color="#ff9900", alpha=0.18, lw=0,
                   label="Zone (≥ 2 Swings)" if i == 0 else None)
        ax.text(1, z.mid, f"{z.touches}×", fontsize=7, color="#b35900", va="center")

    ticks = np.linspace(0, len(d) - 1, 8).astype(int)
    ax.set_xticks(ticks, [d.index[i].strftime("%d.%m.%y") for i in ticks])
    ax.set_xlim(-2, len(d) + 12)
    ax.set_title(f"{symbol} – was der Bot erkennt (Tageskerzen, Swing-Länge {swing_len})", fontsize=12)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.99, 0.01, "▼▲ Swing (bestätigt erst 5 Kerzen später) · — BOS · - - CHoCH",
            transform=ax.transAxes, ha="right", fontsize=8, color="#555")
    fig.tight_layout()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out
