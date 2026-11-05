"""Walk-Forward: Fenster, Variantenwahl nur mit Vergangenheit, Gesamtablauf."""

import pandas as pd
import pytest

from quantswing.backtest.runner import RunConfig, prepare_universe
from quantswing.backtest.walkforward import WFConfig, make_windows, select_variant, walk_forward
from quantswing.data import synthetic_ohlcv


def trades(rs, start, step_days=10, hold_days=5, symbol="AAA"):
    entries = pd.date_range(start, periods=len(rs), freq=f"{step_days}D")
    return pd.DataFrame({
        "symbol": symbol,
        "entry_date": entries.strftime("%Y-%m-%d"),
        "exit_date": (entries + pd.Timedelta(days=hold_days)).strftime("%Y-%m-%d"),
        "r_multiple": rs,
        "exit_reason": ["target" if r > 0 else "stop" for r in rs],
        "bars_held": hold_days, "mae_r": -0.5,
    })


def test_make_windows():
    w = make_windows(2010, 2, pd.Timestamp("2015-06-30"))
    assert [(a.year, b.year) for a, b in w] == [(2010, 2012), (2012, 2014), (2014, 2016)]


def test_select_variant_ignores_trades_after_window_start():
    ws = pd.Timestamp("2015-01-01")
    good_before = trades([1.0, -0.5] * 30, "2012-01-01")
    # Variante B: vor dem Fenster schlecht, danach fantastisch -> darf NICHT gewählt werden
    b = pd.concat([trades([-1.0, 0.5] * 30, "2012-01-01"), trades([5.0] * 50, "2015-02-01")])
    choice, info = select_variant({"A": good_before, "B": b}, ws, min_train_trades=30)
    assert choice == "A"
    assert info["training_trades"] == 60


def test_select_variant_ignores_trades_still_open_at_window_start():
    ws = pd.Timestamp("2015-01-01")
    a = trades([1.0, -0.5] * 30, "2012-01-01")
    # Trade beginnt vor dem Fenster, endet aber erst danach -> zählt nicht
    late = trades([-50.0], "2014-12-30", hold_days=10)
    choice, info = select_variant({"A": pd.concat([a, late])}, ws, 30)
    assert choice == "A" and info["training_trades"] == 60


def test_select_variant_goes_to_cash_if_nothing_profitable():
    ws = pd.Timestamp("2015-01-01")
    choice, info = select_variant({"A": trades([-1.0, 0.5] * 30, "2012-01-01")}, ws, 30)
    assert choice is None and "profitabel" in info["grund"]


def test_select_variant_requires_min_trades():
    choice, info = select_variant({"A": trades([2.0] * 5, "2014-01-01")}, pd.Timestamp("2015-01-01"), 30)
    assert choice is None


@pytest.fixture(scope="module")
def universe():
    data = {f"S{i}": synthetic_ohlcv(n=3200, seed=i, start="2006-01-01") for i in range(8)}
    data["SPY"] = synthetic_ohlcv(n=3200, seed=50, start="2006-01-01")
    cfg = RunConfig(benchmarks=(), crypto_benchmarks=())
    uni = prepare_universe([f"S{i}" for i in range(8)], data.__getitem__, cfg)
    return uni, cfg, data.__getitem__


def test_walk_forward_only_trades_inside_chosen_windows(universe):
    uni, cfg, loader = universe
    res = walk_forward(uni, "trend_pullback", cfg, WFConfig(first_test_year=2010), loader)
    assert "stock" in res.windows
    chosen = {r["fenster"]: r["variante"] for r in res.windows["stock"]}
    if not res.trades.empty:
        entry_years = pd.to_datetime(res.trades["entry_date"]).dt.year
        assert entry_years.min() >= 2010
        labels = list(chosen)
        for _, t in res.trades.iterrows():
            y = pd.Timestamp(t["entry_date"]).year
            assert chosen[labels[(y - 2010) // 2]] == t["variante"]


def test_universe_benchmark(universe):
    from quantswing.backtest.runner import universe_benchmark
    uni, _, _ = universe
    bh = universe_benchmark(uni, "stock", "2010-01-01", "2015-12-31")
    assert set(bh) >= {"rendite_pa_pct", "max_drawdown_pct"}
