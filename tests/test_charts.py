"""Prüf-Chart lässt sich erzeugen (Inhalt wird von Auge geprüft)."""

from quantswing.charts import plot_structure
from quantswing.data import synthetic_ohlcv


def test_plot_structure_writes_png(tmp_path):
    df = synthetic_ohlcv(n=700, seed=4)
    out = plot_structure(df, "DEMO", str(df.index[450].date()), tmp_path / "demo.png")
    assert out.exists() and out.stat().st_size > 10_000
