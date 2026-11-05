"""
Indikatoren: Wertebereiche, bekannte Grenzfälle und – am wichtigsten –
kein Blick in die Zukunft.
"""

import numpy as np
import pandas as pd
import pytest

from quantswing import indicators as ind
from quantswing.data import synthetic_ohlcv
from quantswing.strategies import REGISTRY, get_strategy


@pytest.fixture
def df():
    return synthetic_ohlcv(n=800, seed=3)


def test_rsi_range_and_extremes(df):
    r = ind.rsi(df["Close"]).dropna()
    assert r.between(0, 100).all()
    rising = pd.Series(np.arange(1.0, 50.0))
    assert ind.rsi(rising).iloc[-1] == pytest.approx(100.0)


def test_adx_range(df):
    a = ind.adx(df).dropna()
    assert a["ADX"].between(0, 100).all()
    assert (a["PLUS_DI"] >= 0).all() and (a["MINUS_DI"] >= 0).all()


def test_atr_constant_range():
    idx = pd.bdate_range("2020-01-01", periods=60)
    d = pd.DataFrame({"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.0,
                      "Volume": 1.0}, index=idx)
    assert ind.atr(d).iloc[-1] == pytest.approx(2.0)


def test_donchian_excludes_current_bar(df):
    dh = ind.donchian_high(df["High"], 20)
    assert dh.iloc[30] == df["High"].iloc[10:30].max()


def test_swings_are_only_known_after_confirmation():
    # Spitze an Index 5; mit strength=3 erst ab Index 8 bekannt
    highs = [1, 2, 3, 4, 5, 9, 5, 4, 3, 2, 1, 1]
    idx = pd.bdate_range("2020-01-01", periods=len(highs))
    d = pd.DataFrame({"Open": highs, "High": highs, "Low": [h - 0.5 for h in highs],
                      "Close": highs, "Volume": 1.0}, index=idx, dtype=float)
    sh = ind.confirmed_swings(d, strength=3)["SWING_HIGH"]
    assert sh.iloc[:8].isna().all()
    assert sh.iloc[8] == 9.0


@pytest.mark.parametrize("key", list(REGISTRY))
def test_no_lookahead_in_strategies(key, df):
    """
    Der entscheidende Test: Werden die Daten NACH Tag t verändert, dürfen sich
    Signale und Stops bis Tag t nicht ändern.
    """
    strat = get_strategy(key)
    cut = 600
    rng = np.random.default_rng(0)
    df = df.copy()
    # Marktkontext wie im echten Lauf (Werte beliebig, aber fest)
    df["RS_RANK"] = rng.uniform(0, 1, len(df))
    df["REGIME_OK"] = (rng.uniform(0, 1, len(df)) > 0.3).astype(float)
    full = strat.run(df)
    assert full["signal"].sum() > 0, "Test braucht Signale, sonst prüft er nichts"
    mutated = df.copy()
    mutated.iloc[cut + 1:] *= rng.uniform(0.5, 1.5, size=(len(df) - cut - 1, 1))
    changed = strat.run(mutated)
    pd.testing.assert_series_equal(full["signal"].iloc[: cut + 1], changed["signal"].iloc[: cut + 1])
    pd.testing.assert_series_equal(full["stop"].iloc[: cut + 1], changed["stop"].iloc[: cut + 1])
