"""Portfolio-Simulation: Positionslimits, Rangfolge, Freigabe von Plätzen, Risiko-Begrenzung."""

import pandas as pd
import pytest

from quantswing.backtest.portfolio import PortfolioRules, buy_and_hold, simulate_portfolio


def trade(sym, entry, exit_, r=1.0, prio=0.0, market="US", entry_px=100.0, stop_px=90.0):
    return {"symbol": sym, "entry_date": entry, "exit_date": exit_, "r_multiple": r,
            "priority": prio, "market": market, "entry_price": entry_px, "stop_price": stop_px,
            "exit_reason": "target"}


def test_max_positions_and_priority():
    t = pd.DataFrame([
        trade("A", "2020-01-02", "2020-01-10", prio=0.1),
        trade("B", "2020-01-02", "2020-01-10", prio=0.9),
        trade("C", "2020-01-02", "2020-01-10", prio=0.5),
    ])
    res = simulate_portfolio(t, PortfolioRules(max_positions=2, max_per_market=5))
    assert set(res.taken["symbol"]) == {"B", "C"}      # die zwei stärksten
    assert res.skipped == 1


def test_slot_frees_only_day_after_exit():
    t = pd.DataFrame([
        trade("A", "2020-01-02", "2020-01-06"),
        trade("B", "2020-01-06", "2020-01-10"),   # gleicher Tag wie Ausstieg A -> kein Platz
        trade("C", "2020-01-07", "2020-01-10"),   # Tag danach -> Platz frei
    ])
    res = simulate_portfolio(t, PortfolioRules(max_positions=1, max_per_market=5))
    assert list(res.taken["symbol"]) == ["A", "C"]


def test_max_per_market():
    t = pd.DataFrame([trade(f"S{i}", "2020-01-02", "2020-01-10", market="DE") for i in range(5)])
    res = simulate_portfolio(t, PortfolioRules(max_positions=10, max_per_market=3))
    assert len(res.taken) == 3


def test_no_leverage_caps_risk_for_tight_stops():
    # Stop nur 2 % entfernt: 1 % Risiko bräuchte 50 % des Kontos -> auf 10 % begrenzt
    t = pd.DataFrame([trade("A", "2020-01-02", "2020-01-10", r=-1.0, stop_px=98.0)])
    res = simulate_portfolio(t, PortfolioRules(max_positions=10, risk_per_trade=0.01))
    assert res.taken["risk_pct"].iloc[0] == pytest.approx(0.2)    # 10 % × 2 %
    assert res.stats["endkapital"] == pytest.approx(100_000 * (1 - 0.002))


def test_equity_compounds():
    t = pd.DataFrame([
        trade("A", "2020-01-02", "2020-01-03", r=2.0, stop_px=80.0),
        trade("B", "2020-01-06", "2020-01-07", r=2.0, stop_px=80.0),
    ])
    res = simulate_portfolio(t, PortfolioRules(max_positions=10, risk_per_trade=0.01))
    assert res.stats["endkapital"] == pytest.approx(100_000 * 1.02 * 1.02)


def test_buy_and_hold():
    idx = pd.bdate_range("2020-01-01", periods=300)
    close = pd.Series(range(100, 400), index=idx, dtype=float)
    bh = buy_and_hold(close, "2020-01-01", "2021-12-31")
    assert bh["rendite_pa_pct"] > 0
    assert bh["max_drawdown_pct"] == pytest.approx(0.0)
