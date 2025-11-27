"""MetaTrader 5 execution adapter tailored for FBS demo/live accounts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from loguru import logger

from goldbot.config import settings

try:  # pragma: no cover - optional dependency loaded at runtime
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover
    mt5 = None


OrderSide = Literal["buy", "sell"]


@dataclass
class MT5Adapter:
    server: str | None = None
    login: Optional[int] = None
    password: Optional[str] = None
    symbol: str = "XAUUSD"

    def __post_init__(self) -> None:
        creds = settings.mt5
        self.server = self.server or creds.server
        self.login = self.login or creds.login
        self.password = self.password or creds.password
        self.symbol = self.symbol or creds.symbol

    def connect(self) -> None:
        if mt5 is None:
            raise ImportError("MetaTrader5 package not installed. Run `pip install MetaTrader5`.")
        if not all([self.server, self.login, self.password]):
            raise ValueError("MT5 credentials incomplete. Populate GOLD_MT5__* values.")
        if not mt5.initialize(server=self.server, login=int(self.login), password=self.password):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
        account_info = mt5.account_info()
        logger.info("Connected to MT5 server %s as %s", self.server, account_info.name)

    def shutdown(self) -> None:
        if mt5 is None:
            return
        mt5.shutdown()
        logger.info("MT5 connection closed")

    def place_market_order(
        self,
        side: OrderSide,
        volume: float,
        deviation: int = 20,
        comment: str | None = None,
    ) -> dict:
        """Submit a market order and return MT5 result dictionary."""

        if mt5 is None:
            raise ImportError("MetaTrader5 package not installed.")
        order_type = mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.symbol).ask if side == "buy" else mt5.symbol_info_tick(self.symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": deviation,
            "magic": 4242,
            "comment": comment or "goldbot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        logger.info("Sending MT5 order: %s", request)
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Order failed: {result.retcode} ({result.comment})")
        return result._asdict()

