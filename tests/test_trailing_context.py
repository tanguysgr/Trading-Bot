"""Trailing-Stop, Marktkontext (Regime, relative Stärke) und Strategie-Varianten."""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pytest

from quantswing.backtest.engine import Costs, run_backtest
from quantswing.backtest.runner import RunConfig, prepare_universe
from quantswing.context import asof_before, regime_flag, rs_rank
from quantswing.data import synthetic_ohlcv
from quantswing.strategies import REGISTRY, get_strategy, variants
from quantswing.strategies.base import Strategy

NO_COSTS = Costs(0.0, 0.0)


@dataclass
class TrailOnce(Strategy):
    """Signal an Kerze 0, Stop 90, Trailing mit fester ATR-Spalte."""
    key = "trail_once"
    target_r: float | None = None
    trail_atr: float | None = 2.0
    max_bars: int = 100
    params: dict = field(default_factory=dict)

    def prepare(self, df):
        return df.copy()

    def signals(self, df):
        out = df.copy()
        out["signal"] = False
        out.iloc[0, out.columns.get_loc("signal")] = True
        out["stop"] = 90.0
        return out


def bars(rows, atr=5.0):
    idx = pd.bdate_range("2020-01-01", periods=len(rows))
    df = pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], index=idx, dtype=float)
    df["Volume"] = 1.0
    df["ATR"] = atr
    return df


def test_trailing_stop_follows_high_and_exits():
    rows = [
        (100, 100, 100, 100),   # Signal
        (100, 104, 99, 103),    # Einstieg 100; Stop danach max(90, 104-10=94) = 94
        (103, 120, 102, 118),   # Hoch 120 -> Stop ab morgen 110
        (118, 119, 111, 112),   # Tief 111 > 110: hält; Stop bleibt 110
        (112, 113, 108, 109),   # Tief 108 <= 110 -> Ausstieg zu 110
    ]
    t = run_backtest(bars(rows), TrailOnce(), costs=NO_COSTS)[0]
    assert t.exit_reason == "trail"
    assert t.exit_price == pytest.approx(110.0)
    assert t.r_multiple == pytest.approx(1.0)          # (110-100)/(100-90)
    assert np.isnan(t.target_price)


def test_trailing_stop_is_not_used_on_the_bar_that_sets_it():
    # Kerze 2 macht Hoch 120 UND fällt bis 109: der neue Stop (110) darf erst morgen gelten
    rows = [(100, 100, 100, 100), (100, 104, 99, 103), (103, 120, 109, 115), (115, 116, 114, 115)]
    trades = run_backtest(bars(rows), TrailOnce(), costs=NO_COSTS)
    assert trades[0].exit_reason == "end_of_data"


def test_trailing_stop_never_moves_down():
    rows = [(100, 100, 100, 100), (100, 120, 100, 119), (119, 121, 112, 113)]
    df = bars(rows)
    df.iloc[1, df.columns.get_loc("ATR")] = 5.0     # Stop -> 110
    df.iloc[2, df.columns.get_loc("ATR")] = 50.0    # ATR explodiert: Kandidat 21 -> ignoriert
    rows.append((113, 114, 109, 110))
    df = pd.concat([df, bars([rows[-1]]).set_index(pd.DatetimeIndex([df.index[-1] + pd.offsets.BDay()]))])
    t = run_backtest(df, TrailOnce(), costs=NO_COSTS)[0]
    assert t.exit_reason == "trail" and t.exit_price == pytest.approx(110.0)


def test_asof_before_uses_strictly_earlier_values():
    src = pd.Series([1.0, 2.0, 3.0], index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]))
    tgt = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    assert list(asof_before(src, tgt)) == [1.0, 2.0, 3.0]


def test_regime_flag():
    close = pd.Series(np.r_[np.full(200, 100.0), 110.0, 90.0],
                      index=pd.bdate_range("2020-01-01", periods=202))
    f = regime_flag(close)
    assert f.iloc[:199].isna().all()
    assert f.iloc[200] == 1.0 and f.iloc[201] == 0.0


def test_rs_rank_orders_and_is_lagged():
    idx = pd.bdate_range("2020-01-01", periods=300)
    closes = {f"S{i}": pd.Series(100 * (1 + 0.001 * i) ** np.arange(300), index=idx) for i in range(25)}
    ranks = rs_rank(closes)
    last = {s: r.iloc[-1] for s, r in ranks.items()}
    assert last["S24"] == pytest.approx(1.0) and last["S0"] == pytest.approx(1 / 25)
    # Tag 126 ist der erste mit 126-Tage-Rendite; wegen Verzögerung erst ab Tag 127 sichtbar
    assert np.isnan(ranks["S0"].iloc[126]) and not np.isnan(ranks["S0"].iloc[127])


def test_prepare_universe_adds_context_without_lookahead():
    data = {f"S{i}": synthetic_ohlcv(n=600, seed=i) for i in range(6)}
    data["SPY"] = synthetic_ohlcv(n=600, seed=99)
    cfg = RunConfig(min_turnover_usd=0)
    uni = prepare_universe([f"S{i}" for i in range(6)], data.__getitem__, cfg)
    df = uni.data["S0"]
    assert {"RS_RANK", "REGIME_OK"} <= set(df.columns)
    # Regime am Tag t entspricht dem SPY-Flag vom Vortag
    flag = regime_flag(data["SPY"]["Close"])
    assert df["REGIME_OK"].iloc[400] == flag.iloc[399]


def test_get_strategy_merges_params_and_rejects_typos():
    s = get_strategy("trend_pullback", params={"use_regime": True}, target_r=None, trail_atr=3.0)
    assert s.params["use_regime"] is True and s.params["adx_min"] == 20.0
    assert s.target_r is None and s.trail_atr == 3.0
    with pytest.raises(KeyError):
        get_strategy("trend_pullback", params={"adx_mni": 5})
    with pytest.raises(KeyError):
        get_strategy("trend_pullback", foo=1)


@pytest.mark.parametrize("key", list(REGISTRY))
def test_all_variants_build_and_have_no_lookahead(key):
    df = synthetic_ohlcv(n=800, seed=10)
    rng = np.random.default_rng(1)
    df["RS_RANK"] = rng.uniform(0, 1, len(df))
    df["REGIME_OK"] = 1.0
    cut = 600
    for label, strat in variants(key):
        full = strat.run(df)
        mutated = df.copy()
        mutated.iloc[cut + 1:, :5] *= 1.3
        changed = strat.run(mutated)
        assert (full["signal"].iloc[:cut + 1] == changed["signal"].iloc[:cut + 1]).all(), label
        trades = run_backtest(df, strat, "X")
        assert all(np.isfinite(t.r_multiple) for t in trades), label
