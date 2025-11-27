import pandas as pd

from goldbot.config import settings
from goldbot.data.loaders import save_price_data
from goldbot.data.quality import compute_quality_report


def test_save_price_data(tmp_path):
    settings.data.raw_dir = tmp_path
    df = pd.DataFrame(
        {"open": [1], "high": [1], "low": [1], "close": [1], "volume": [10]},
        index=pd.date_range("2024-01-01", periods=1, freq="H"),
    )
    path = save_price_data(df, symbol="XAU/USD", timeframe="1h", provider="test", fmt="parquet")
    assert path.exists()


def test_compute_quality_report():
    idx = pd.date_range("2024-01-01", periods=5, freq="H", tz="UTC")
    df = pd.DataFrame({"close": range(5)}, index=idx.delete(2))
    report = compute_quality_report(df, freq="1H")
    assert report.n_rows == 4
    assert report.missing_rows == 1

