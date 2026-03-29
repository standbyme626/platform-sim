import pytest
from providers.base.provider import BaseProvider, ProviderMode


def test_provider_mode_enum():
    assert ProviderMode.MOCK.value == "mock"
    assert ProviderMode.REAL.value == "real"


def test_base_provider_mode_switch():
    class TestProvider(BaseProvider):
        def get_order(self, order_id: str):
            return {}

        def list_orders(self, page: int = 1, page_size: int = 20):
            return {}

        def get_shipment(self, order_id: str):
            return {}

        def get_refund(self, refund_id: str):
            return {}

        def create_refund(self, order_id: str, reason: str, amount: str):
            return {}

        def get_conversation(self, conversation_id: str):
            return {}

        def list_messages(self, conversation_id: str, limit: int = 100):
            return {}

    provider = TestProvider(ProviderMode.MOCK)
    assert provider.is_mock() is True
    assert provider.is_real() is False

    provider.switch_mode(ProviderMode.REAL)
    assert provider.is_mock() is False
    assert provider.is_real() is True
