import pandas as pd
import pytest

from quantswing.backtest.metrics import (
    GATES, compute_metrics, max_drawdown, wilson_lower_bound,
)
from quantswing.backtest.runner import evaluate


def frame(rs, symbol="AAPL", start="2015-01-01"):
    dates = pd.bdate_range(start, periods=len(rs) * 5)[::5]
    return pd.DataFrame({
        "symbol": symbol,
        "entry_date": dates.strftime("%Y-%m-%d"),
        "exit_date": (dates + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
        "r_multiple": rs,
        "exit_reason": ["target" if r > 0 else "stop" for r in rs],
        "bars_held": 3,
        "mae_r": -0.3,
    })


def test_basic_metrics():
    m = compute_metrics(frame([2.0, -1.0, 2.0, -1.0]))
    assert m.trades == 4
    assert m.winrate == pytest.approx(50.0)
    assert m.expectancy_r == pytest.approx(0.5)
    assert m.profit_factor == pytest.approx(2.0)


def test_open_trades_excluded():
    f = frame([2.0, -1.0, 0.7])
    f.loc[2, "exit_reason"] = "end_of_data"
    m = compute_metrics(f)
    assert m.trades == 2 and m.open_trades == 1


def test_wilson_is_conservative():
    assert wilson_lower_bound(6, 10) < 0.6
    assert wilson_lower_bound(600, 1000) > wilson_lower_bound(6, 10)


def test_drawdown():
    eq = pd.Series([1.0, 1.2, 0.9, 1.1])
    assert max_drawdown(eq) == pytest.approx(-25.0)


def test_crypto_gate_is_stricter_than_stock():
    s, c = GATES["stock"], GATES["crypto"]
    assert c.min_profit_factor > s.min_profit_factor
    assert c.min_expectancy_lower_r > s.min_expectancy_lower_r
    assert c.min_winrate_lower > s.min_winrate_lower


def test_evaluate_separates_asset_classes_and_periods():
    trades = pd.concat([
        frame([1.5, -1.0] * 40, "AAPL", "2012-01-01"),
        frame([1.5, -1.0] * 40, "BTC-USD", "2012-01-01"),
    ], ignore_index=True)
    res = evaluate(trades, "2013-01-01")
    assert set(res) == {"stock", "crypto"}
    blk = res["stock"]
    assert blk["training"]["trades"] + blk["test"]["trades"] == blk["gesamt"]["trades"]
