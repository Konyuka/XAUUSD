"""Twelve Data REST client for historical XAU/USD prices."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Iterable, Optional

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from goldbot.config import settings

LOGGER = logging.getLogger(__name__)


class TwelveDataClient:
    """Thin convenience wrapper around Twelve Data's REST API."""

    BASE_URL = "https://api.twelvedata.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key or settings.providers.twelvedata_api_key
        if not self.api_key:
            raise ValueError("Twelve Data API key missing. Set GOLD_PROVIDERS__TWELVEDATA_API_KEY.")
        self.session = session or requests.Session()

    def fetch_time_series(
        self,
        symbol: str | None = None,
        interval: str | None = None,
        outputsize: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        timezone: str = "UTC",
    ) -> pd.DataFrame:
        """Return OHLCV dataframe for the requested symbol/timeframe."""

        params: dict[str, Any] = {
            "symbol": symbol or settings.providers.default_symbol,
            "interval": interval or settings.providers.default_interval,
            "outputsize": outputsize or settings.providers.outputsize,
            "timezone": timezone,
            "apikey": self.api_key,
            "order": "ASC",
            "format": "JSON",
        }
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        values = list(self._paginate("time_series", params))
        if not values:
            raise RuntimeError("Twelve Data response empty.")

        df = pd.DataFrame(values)
        df.rename(columns=str.lower, inplace=True)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        numeric_cols = [col for col in ["open", "high", "low", "close", "volume"] if col in df.columns]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        if "volume" not in df.columns:
            df["volume"] = 0.0
        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True)
        return df

    def _paginate(self, endpoint: str, params: dict[str, Any]) -> Iterable[dict[str, Any]]:
        next_token: Optional[str] = None
        while True:
            if next_token:
                params["page"] = next_token
            payload = self._get(endpoint, params)
            status = payload.get("status")
            if status != "ok":
                raise RuntimeError(payload.get("message", "Twelve Data error"))
            values = payload.get("values") or []
            for item in values:
                yield item
            next_token = payload.get("next_page")
            if not next_token:
                break

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        LOGGER.debug("Requesting Twelve Data endpoint %s with params %s", endpoint, params)
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

