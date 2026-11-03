import sys
import types

import numpy as np
import pandas as pd

from quantswing.data import asset_class, clean_ohlcv, load_ohlcv, synthetic_ohlcv


def test_asset_class():
    assert asset_class("BTC-USD") == "crypto"
    assert asset_class("SAP.DE") == "stock"
    assert asset_class("7203.T") == "stock"


def test_clean_removes_broken_rows():
    df = synthetic_ohlcv(n=50)
    df.iloc[5, df.columns.get_loc("Close")] = np.nan
    df.iloc[6, df.columns.get_loc("Low")] = -1.0
    df.iloc[7, df.columns.get_loc("High")] = 0.5 * df.iloc[7]["Low"]
    out = clean_ohlcv(df, "TEST")
    assert len(out) == 47
    assert (out["High"] >= out[["Open", "Close"]].max(axis=1)).all()
    assert (out["Low"] <= out[["Open", "Close"]].min(axis=1)).all()


def test_load_handles_yfinance_multiindex_and_caches(tmp_path, monkeypatch):
    calls = {"n": 0}
    base = synthetic_ohlcv(n=30)

    def fake_download(symbol, **kw):
        calls["n"] += 1
        df = base.copy()
        df.columns = pd.MultiIndex.from_product([df.columns, [symbol]])
        return df

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=fake_download))
    a = load_ohlcv("AAPL", cache_dir=tmp_path)
    b = load_ohlcv("AAPL", cache_dir=tmp_path)
    assert calls["n"] == 1                       # zweiter Aufruf kommt aus dem Cache
    assert list(a.columns) == ["Open", "High", "Low", "Close", "Volume"]
    pd.testing.assert_frame_equal(a, b, check_freq=False)
