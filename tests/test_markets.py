"""Märkte, Währungen, Liquiditätsfilter und Universumsdateien."""

import numpy as np
import pandas as pd
import pytest

from dataclasses import dataclass, field

from quantswing.backtest.engine import Costs, run_backtest
from quantswing.data import turnover_usd
from quantswing.markets import asset_class, currency_of, fx_symbol, market_of
from quantswing.strategies.base import Strategy
from quantswing.universe import read_universe


@pytest.mark.parametrize("sym,code,cur", [
    ("AAPL", "US", "USD"), ("BRK-B", "US", "USD"), ("SAP.DE", "DE", "EUR"),
    ("AZN.L", "UK", "GBP"), ("7203.T", "JP", "JPY"), ("0700.HK", "HK", "HKD"),
    ("BTC-USD", "CRYPTO", "USD"), ("NOVO-B.CO", "DK", "DKK"),
])
def test_market_of(sym, code, cur):
    assert market_of(sym).code == code
    assert currency_of(sym) == cur


def test_asset_class_and_fx_symbol():
    assert asset_class("ETH-USD") == "crypto"
    assert asset_class("BRK-B") == "stock"          # Bindestrich allein ist kein Krypto
    assert fx_symbol("EUR") == "EURUSD=X"
    assert fx_symbol("USD") is None


def _px(close, volume, n=100):
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close,
                         "Volume": volume}, index=idx, dtype=float)


def test_turnover_converts_currency_and_pence():
    df = _px(200.0, 100_000)                     # 200 Pence × 100k = 200k GBP
    fx = pd.Series(1.25, index=df.index)         # 1 GBP = 1,25 USD
    t = turnover_usd(df, "AZN.L", fx)
    assert t.iloc[-1] == pytest.approx(200 / 100 * 100_000 * 1.25)


def test_turnover_without_fx_is_unknown():
    df = _px(10.0, 1000)
    assert turnover_usd(df, "SAP.DE", None).isna().all()


def test_turnover_uses_only_past():
    df = _px(10.0, 1000.0)
    t1 = turnover_usd(df, "AAPL")
    df2 = df.copy()
    df2.iloc[60:, df2.columns.get_loc("Volume")] = 1e9
    t2 = turnover_usd(df2, "AAPL")
    pd.testing.assert_series_equal(t1.iloc[:60], t2.iloc[:60])


@dataclass
class AlwaysSignal(Strategy):
    key = "always"
    max_bars: int = 2
    params: dict = field(default_factory=dict)

    def prepare(self, df):
        return df.copy()

    def signals(self, df):
        out = df.copy()
        out["signal"] = True
        out["stop"] = out["Close"] * 0.9
        return out


def test_tradable_mask_blocks_signals():
    df = _px(np.linspace(100, 120, 30), 1000, n=30)
    df["High"] *= 1.001
    blocked = pd.Series(False, index=df.index)
    assert run_backtest(df, AlwaysSignal(), "X", Costs(0, 0), blocked) == []
    assert len(run_backtest(df, AlwaysSignal(), "X", Costs(0, 0), None)) > 0


def test_read_universe(tmp_path):
    f = tmp_path / "u.txt"
    f.write_text("# Kommentar\nAAPL msft  # zwei pro Zeile\n\nSAP.DE AAPL\n", encoding="utf-8")
    assert read_universe(f) == ["AAPL", "MSFT", "SAP.DE"]
