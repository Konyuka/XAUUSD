"""Utilities to verify MT5 connectivity before running live trades."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Literal, Optional

from loguru import logger

from goldbot.execution.mt5_adapter import MT5Adapter
from goldbot.utils.logging import configure_logging

try:  # pragma: no cover - runtime dependency
    import MetaTrader5 as mt5  # type: ignore
except ImportError:  # pragma: no cover
    mt5 = None


@dataclass(slots=True)
class MT5SmokeResult:
    balance: float
    equity: float
    margin_free: float
    server: str
    login: int
    order_result: Optional[dict]


def run_mt5_smoke_test(
    place_order: bool = False,
    side: Literal["buy", "sell"] = "buy",
    volume: float = 0.01,
) -> MT5SmokeResult:
    """Connect to MT5, fetch account info, optionally send a small market order."""

    if mt5 is None:
        raise ImportError("MetaTrader5 package missing. Install on Windows with Python <=3.12.")

    adapter = MT5Adapter()
    adapter.connect()
    info = mt5.account_info()._asdict()
    order = None
    if place_order:
        logger.info("Placing MT5 %s order for %.2f lots", side, volume)
        order = adapter.place_market_order(side=side, volume=volume, comment="goldbot-smoke")
    adapter.shutdown()
    return MT5SmokeResult(
        balance=info.get("balance", 0.0),
        equity=info.get("equity", 0.0),
        margin_free=info.get("margin_free", 0.0),
        server=info.get("server", ""),
        login=info.get("login", 0),
        order_result=order,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test MT5 connectivity with optional trade.")
    parser.add_argument("--place-order", action="store_true", help="Submit a tiny market order.")
    parser.add_argument("--side", choices=["buy", "sell"], default="buy")
    parser.add_argument("--volume", type=float, default=0.01)
    args = parser.parse_args()

    configure_logging()
    result = run_mt5_smoke_test(place_order=args.place_order, side=args.side, volume=args.volume)
    print("Account:", result)


if __name__ == "__main__":
    main()

