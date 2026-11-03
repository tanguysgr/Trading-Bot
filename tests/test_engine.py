"""
Prüft die Ausführungsregeln der Backtest-Engine an handgebauten Kursverläufen.
Jeder Test entspricht einer Regel aus quantswing/backtest/engine.py.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pytest

from quantswing.backtest.engine import Costs, run_backtest
from quantswing.strategies.base import Strategy

NO_COSTS = Costs(commission=0.0, slippage=0.0)


@dataclass
class FixedSignal(Strategy):
    """Testsignal an vorgegebenen Kerzen mit festem Stop."""
    key = "fixed"
    target_r: float = 2.0
    max_bars: int = 100
    params: dict = field(default_factory=lambda: {"at": [0], "stop": 95.0})

    def prepare(self, df):
        return df.copy()

    def signals(self, df):
        out = df.copy()
        out["signal"] = False
        out.iloc[self.params["at"], out.columns.get_loc("signal")] = True
        out["stop"] = self.params["stop"]
        return out


def bars(rows):
    """rows: Liste von (open, high, low, close)."""
    idx = pd.bdate_range("2020-01-01", periods=len(rows))
    df = pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], index=idx, dtype=float)
    df["Volume"] = 1000.0
    return df


def test_entry_is_next_open_not_signal_close():
    df = bars([(100, 101, 99, 100), (102, 103, 101, 102), (102, 103, 101, 102)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.entry_date == df.index[1]
    assert t.entry_price == 102.0          # Eröffnung Tag 2, nicht Schluss Tag 1


def test_target_hit():
    # Einstieg 100, Stop 95 -> Risiko 5, Ziel 110
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (101, 111, 100, 110)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.exit_reason == "target"
    assert t.exit_price == 110.0
    assert t.r_multiple == pytest.approx(2.0)


def test_stop_hit():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (99, 99, 94, 95)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.exit_reason == "stop"
    assert t.r_multiple == pytest.approx(-1.0)


def test_stop_wins_if_both_hit_same_bar():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (100, 112, 94, 105)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.exit_reason == "stop"


def test_gap_through_stop_fills_at_worse_open():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (90, 92, 89, 91)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.exit_reason == "stop_gap"
    assert t.exit_price == 90.0
    assert t.r_multiple == pytest.approx(-2.0)   # schlechter als geplant


def test_gap_over_target_fills_at_better_open():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (115, 116, 114, 115)])
    t = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    assert t.exit_reason == "target_gap"
    assert t.r_multiple == pytest.approx(3.0)


def test_skip_trade_if_open_already_below_stop():
    df = bars([(100, 100, 100, 100), (94, 95, 93, 94), (94, 95, 93, 94)])
    assert run_backtest(df, FixedSignal(), costs=NO_COSTS) == []


def test_time_stop():
    rows = [(100, 100, 100, 100)] + [(100, 101, 99, 100)] * 10
    strat = FixedSignal(max_bars=3)
    t = run_backtest(bars(rows), strat, costs=NO_COSTS)[0]
    assert t.exit_reason == "time"
    assert t.bars_held == 3


def test_only_one_position_per_symbol():
    rows = [(100, 101, 99, 100)] * 6
    strat = FixedSignal(params={"at": [0, 1, 2], "stop": 95.0})
    trades = run_backtest(bars(rows), strat, costs=NO_COSTS)
    assert len(trades) == 1
    assert trades[0].exit_reason == "end_of_data"


def test_costs_reduce_result():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (101, 111, 100, 110)])
    clean = run_backtest(df, FixedSignal(), costs=NO_COSTS)[0]
    costly = run_backtest(df, FixedSignal(), costs=Costs(0.001, 0.0005))[0]
    assert costly.r_multiple < clean.r_multiple
    assert costly.entry_price > 100.0          # Slippage beim Kauf
    assert costly.exit_price < costly.target_price   # Slippage beim Verkauf


def test_short_mirrors_long():
    df = bars([(100, 100, 100, 100), (100, 101, 99, 100), (99, 100, 89, 90)])
    strat = FixedSignal(direction="SHORT", params={"at": [0], "stop": 105.0})
    t = run_backtest(df, strat, costs=NO_COSTS)[0]
    assert t.exit_reason == "target"
    assert t.r_multiple == pytest.approx(2.0)
