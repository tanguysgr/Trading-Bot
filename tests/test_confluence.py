"""Confluence-Strategie: Spiegelung Long/Short, Regeln, Begründungen."""

import numpy as np
import pandas as pd
import pytest

from quantswing.backtest.engine import Costs, run_backtest
from quantswing.data import synthetic_ohlcv
from quantswing.strategies import get_strategy


def mirrored(df: pd.DataFrame) -> pd.DataFrame:
    """Exakte Spiegelung mit positiven Preisen: P' = K − P."""
    k = 2 * df["High"].max()
    out = df.copy()
    out["Open"], out["Close"] = k - df["Open"], k - df["Close"]
    out["High"], out["Low"] = k - df["Low"], k - df["High"]
    return out, k


@pytest.mark.parametrize("seed", [1, 8, 10])
def test_short_is_exact_mirror_of_long(seed):
    df = synthetic_ohlcv(n=1500, seed=seed)
    m, k = mirrored(df)
    lo = get_strategy("confluence_long").run(df)
    sh = get_strategy("confluence_short").run(m)
    assert lo["signal"].sum() > 0
    assert (lo["signal"] == sh["signal"]).all()
    sig = lo["signal"]
    np.testing.assert_allclose(sh.loc[sig, "stop"], k - lo.loc[sig, "stop"], rtol=1e-9)


def test_signal_rules_hold():
    df = synthetic_ohlcv(n=3000, seed=4)
    s = get_strategy("confluence_long")
    out = s.run(df)
    sig = out[out["signal"]]
    assert len(sig) > 0
    assert (sig["Close"] > sig["Open"]).all()                     # grüne Bestätigungskerze
    assert (sig["W_SMA50"] > sig["W_SMA200"]).all()                # Trend
    assert (sig["Close"] > sig["W_SMA200"]).all()
    risk = sig["Close"] - sig["stop"]
    assert (risk >= 1.0 * sig["ATR"] - 1e-9).all()                 # Stop mind. 1 ATR
    assert (risk <= 3.0 * sig["ATR"] + 1e-9).all()                 # höchstens 3 ATR
    assert all(len(s.explain(r)) >= 4 for _, r in sig.iterrows())  # Begründung vorhanden


def test_variants_are_stricter_than_base():
    df = synthetic_ohlcv(n=3000, seed=4)
    base = get_strategy("confluence_long").run(df)["signal"]
    cluster = get_strategy("confluence_long", params={"min_types": 2}).run(df)["signal"]
    internal = get_strategy("confluence_long", params={"need_internal": True}).run(df)["signal"]
    assert cluster.sum() <= base.sum() and not (cluster & ~base).any()
    assert internal.sum() <= base.sum() and not (internal & ~base).any()


def test_trades_have_target_at_1_25_r():
    df = synthetic_ohlcv(n=3000, seed=4)
    s = get_strategy("confluence_long")
    t = run_backtest(df, s, "X", Costs(0, 0))[0]
    assert (t.target_price - t.entry_price) == pytest.approx(1.25 * (t.entry_price - t.stop_price))
