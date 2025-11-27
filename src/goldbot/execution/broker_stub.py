"""Execution adapters (paper trading placeholder)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from loguru import logger


OrderSide = Literal["buy", "sell"]


@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: float
    price: float | None = None
    order_type: Literal["market", "limit"] = "market"


class BrokerStub:
    """Simple stub that logs orders instead of sending to a broker."""

    def submit(self, order: Order) -> str:
        order_id = f"stub-{order.symbol}-{order.side}"
        logger.info("Submitting order {}", order)
        return order_id

    def cancel(self, order_id: str) -> None:
        logger.info("Cancel order {}", order_id)

