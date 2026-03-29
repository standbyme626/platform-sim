from typing import Dict, Any, Optional, List
import httpx
from providers.base.provider import BaseProvider, ProviderMode


class TaobaoProvider(BaseProvider):
    def __init__(
        self,
        mode: ProviderMode = ProviderMode.MOCK,
        app_key: str = "test_app_key",
        app_secret: str = "test_app_secret",
        base_url: str = "https://api.taobao.com",
    ):
        super().__init__(mode)
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = base_url
        self.access_token: Optional[str] = None

    def get_order(self, order_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_order(order_id)
        return self._real_get_order(order_id)

    def _mock_get_order(self, order_id: str) -> Dict[str, Any]:
        return {
            "trade": {
                "tid": order_id,
                "status": "wait_ship",
                "total_fee": "99.99",
                "payment": "99.99",
                "receiver_name": "张三",
                "receiver_phone": "138****8000",
                "receiver_address": "浙江省杭州市余杭区",
                "created": "2026-03-01 10:00:00",
                "modified": "2026-03-29 12:00:00",
            },
            "orders": {
                "order": [
                    {
                        "oid": f"{order_id}_1",
                        "status": "wait_ship",
                        "title": "测试商品",
                        "price": "99.99",
                        "num": 1,
                    }
                ]
            },
        }

    async def _real_get_order(self, order_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/router/rest",
                params={
                    "method": "taobao.trade.get",
                    "app_key": self.app_key,
                    "session": self.access_token,
                    "tid": order_id,
                },
            )
            return response.json()

    def list_orders(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_list_orders(page, page_size)
        return self._real_list_orders(page, page_size)

    def _mock_list_orders(self, page: int, page_size: int) -> Dict[str, Any]:
        return {
            "trades": {
                "trade": [
                    {
                        "tid": f"TB_ORDER_{page}_{i}",
                        "status": "wait_ship",
                        "total_fee": "99.99",
                    }
                    for i in range(page_size)
                ]
            },
            "total_results": 100,
            "page_no": page,
            "page_size": page_size,
        }

    def get_shipment(self, order_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_shipment(order_id)
        return self._real_get_shipment(order_id)

    def _mock_get_shipment(self, order_id: str) -> Dict[str, Any]:
        return {
            "sid": f"SID_{order_id}",
            "status": "shipped",
            "company_name": "顺丰速运",
            "out_sid": "SF1234567890",
            "send_time": "2026-03-15 14:00:00",
            "receiver_name": "张三",
            "receiver_phone": "138****8000",
            "receiver_address": "浙江省杭州市余杭区",
        }

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_refund(refund_id)
        return self._real_get_refund(refund_id)

    def _mock_get_refund(self, refund_id: str) -> Dict[str, Any]:
        return {
            "refund_id": refund_id,
            "status": "refunding",
            "reason": "商品损坏",
            "description": "商品在运输过程中损坏",
            "refund_fee": "99.99",
            "created": "2026-03-20 10:00:00",
            "modified": "2026-03-29 12:00:00",
        }

    def create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_create_refund(order_id, reason, amount)
        return self._real_create_refund(order_id, reason, amount)

    def _mock_create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        return {
            "refund_id": f"REFUND_{order_id}",
            "order_id": order_id,
            "status": "refunding",
            "reason": reason,
            "refund_fee": amount,
            "created": "2026-03-29 12:00:00",
        }

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Taobao does not support conversation API")

    def list_messages(self, conversation_id: str, limit: int = 100) -> Dict[str, Any]:
        raise NotImplementedError("Taobao does not support message API")
