from goldbot.config import settings
from goldbot.execution.smoke import run_mt5_smoke_test


class DummyInfo(dict):
    def _asdict(self):
        return self


class DummyResult:
    retcode = 1
    comment = "done"

    def _asdict(self):
        return {"ticket": 1}


class DummyTick:
    bid = 1900.0
    ask = 1900.5


class DummyMT5Module:
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    TRADE_ACTION_DEAL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 0
    TRADE_RETCODE_DONE = 1

    @staticmethod
    def initialize(**kwargs):
        return True

    @staticmethod
    def shutdown():
        return True

    @staticmethod
    def account_info():
        return DummyInfo(balance=1_000_000, equity=1_000_100, margin_free=900_000, server="FBS-Demo", login=105268265)

    @staticmethod
    def symbol_info_tick(symbol):
        return DummyTick()

    @staticmethod
    def order_send(request):
        return DummyResult()


def test_run_mt5_smoke(monkeypatch):
    dummy = DummyMT5Module()
    monkeypatch.setattr("goldbot.execution.mt5_adapter.mt5", dummy)
    monkeypatch.setattr("goldbot.execution.smoke.mt5", dummy)

    settings.mt5.login = 105268265
    settings.mt5.password = "pwd"

    result = run_mt5_smoke_test(place_order=True, volume=0.01)
    assert result.balance == 1_000_000
    assert result.order_result["ticket"] == 1

