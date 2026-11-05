"""Swings, BOS/CHoCH, Fibonacci-Schenkel und Zonen – Korrektheit und kein Blick in die Zukunft."""

import numpy as np
import pandas as pd
import pytest

from quantswing import indicators as ind
from quantswing.data import synthetic_ohlcv
from quantswing.structure import (
    LONG, SHORT, PivotBook, cluster_zones, fib_legs, fib_price, market_structure, pivots, zones_at,
)

# Linienchart (High = Low = Close) mit klaren Swings, siehe Kommentare in den Tests
LINE = [20, 19, 18, 17, 18, 19, 18, 17, 16, 15, 16, 17, 16, 15, 14,
        15, 16, 17, 18, 19, 20, 21, 20, 19, 18, 19, 20, 21, 22, 23]


def line_df(values):
    idx = pd.bdate_range("2020-01-01", periods=len(values))
    v = np.asarray(values, dtype=float)
    return pd.DataFrame({"Open": v, "High": v, "Low": v, "Close": v, "Volume": 1.0}, index=idx)


def test_pivots_are_reported_only_when_confirmed():
    piv = pivots(line_df(LINE), left=2, right=2)
    # Swing-Hoch an Kerze 5 (19) ist erst an Kerze 7 bekannt
    assert np.isnan(piv["PH"].iloc[5]) and piv["PH"].iloc[7] == 19 and piv["PH_BAR"].iloc[7] == 5
    assert list(piv["PH"].dropna()) == [19, 17, 21]
    assert list(piv["PL"].dropna()) == [17, 15, 14, 18]


def test_equal_highs_count_once():
    piv = pivots(line_df([1, 2, 5, 5, 2, 1, 1]), left=2, right=2)
    assert list(piv["PH_BAR"].dropna()) == [2]


def test_bos_and_choch_sequence():
    ms = market_structure(line_df(LINE), left=2, right=2)
    events = {i: e for i, e in enumerate(ms["EVENT"]) if e != 0}
    # Kerze 8: erster Bruch nach unten (noch kein Trend) = BOS ↓
    # Kerze 14: weiterer Bruch nach unten = BOS ↓
    # Kerze 18: erster Bruch nach oben im Abwärtstrend = CHoCH ↑
    # Kerze 28: weiterer Bruch nach oben = BOS ↑
    assert events == {8: -1, 14: -1, 18: 2, 28: 1}
    assert ms["BIAS"].iloc[17] == SHORT and ms["BIAS"].iloc[18] == LONG


def test_fib_legs_from_last_important_low():
    df = line_df(LINE)
    atr = pd.Series(0.5, index=df.index)
    legs = fib_legs(df, pivots(df, 2, 2), atr, min_leg_atr=3.0)
    # Swing-Hoch 21 (Kerze 21) bestätigt an Kerze 23; wichtigstes Tief seit
    # dem vorherigen Swing-Hoch (Kerze 11) ist 14
    assert legs["UP_HI"].iloc[23] == 21 and legs["UP_LO"].iloc[23] == 14
    assert legs["UP_HI"].iloc[29] == 21                       # bleibt aktiv
    # Short-Schenkel 21 -> 18 entsteht an Kerze 26 und erlischt, als der Kurs über 21 schließt
    assert legs["DN_HI"].iloc[26] == 21 and legs["DN_LO"].iloc[26] == 18
    assert np.isnan(legs["DN_HI"].iloc[28])
    assert fib_price(21, 14, 0.618, LONG) == pytest.approx(21 - 0.618 * 7)
    assert fib_price(21, 18, 0.5, SHORT) == pytest.approx(19.5)


def test_fib_leg_needs_minimum_size():
    df = line_df(LINE)
    legs = fib_legs(df, pivots(df, 2, 2), pd.Series(5.0, index=df.index), min_leg_atr=3.0)
    assert legs["UP_HI"].isna().all()


def test_cluster_zones():
    zones = cluster_zones(np.array([10.0, 10.3, 12.0, 15.0, 15.2, 15.4]), merge_dist=0.5, pad=0.1)
    assert [(round(z.bottom, 2), round(z.top, 2), z.touches) for z in zones] == [(9.9, 10.4, 2), (14.9, 15.5, 3)]


def test_pivot_book_respects_known_at_and_lookback():
    piv = pivots(line_df(LINE), 2, 2)
    book = PivotBook(piv)
    assert sorted(book.active(6)) == [17]                     # nur das Tief von Kerze 3
    assert sorted(book.active(13)) == [15, 17, 17, 19]
    assert sorted(book.active(13, lookback=5)) == [15, 17]    # Swings ab Kerze 8


@pytest.mark.parametrize("cut", [300, 450, 599])
def test_no_lookahead_in_building_blocks(cut):
    df = synthetic_ohlcv(n=600, seed=11)
    part = df.iloc[: cut + 1]

    full_piv, part_piv = pivots(df), pivots(part)
    pd.testing.assert_frame_equal(full_piv.iloc[: cut + 1], part_piv)

    pd.testing.assert_frame_equal(market_structure(df).iloc[: cut + 1], market_structure(part))

    full_atr, part_atr = ind.atr(df), ind.atr(part)
    pd.testing.assert_frame_equal(fib_legs(df, full_piv, full_atr).iloc[: cut + 1],
                                  fib_legs(part, part_piv, part_atr))

    zf = zones_at(PivotBook(full_piv), cut, full_atr.iloc[cut])
    zp = zones_at(PivotBook(part_piv), cut, part_atr.iloc[cut])
    assert zf == zp
