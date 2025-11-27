import pandas as pd

from goldbot.data.twelvedata_client import TwelveDataClient


def test_fetch_time_series(requests_mock):
    client = TwelveDataClient(api_key="demo-key")
    requests_mock.get(
        "https://api.twelvedata.com/time_series",
        json={
            "status": "ok",
            "values": [
                {"datetime": "2024-01-01 00:00:00", "open": "2000", "high": "2010", "low": "1995", "close": "2005", "volume": "100"},
                {"datetime": "2024-01-01 01:00:00", "open": "2005", "high": "2015", "low": "2000", "close": "2010", "volume": "120"},
            ],
        },
    )
    df = client.fetch_time_series(symbol="XAU/USD", interval="1h", outputsize=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["close"] == 2005.0

