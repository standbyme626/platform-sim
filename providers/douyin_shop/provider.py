from typing import Dict, Any, Optional, List
import httpx
import hashlib
import time
from providers.base.provider import BaseProvider, ProviderMode


class DouyinShopProvider(BaseProvider):
    def __init__(
        self,
        mode: ProviderMode = ProviderMode.MOCK,
        app_key: str = "test_app_key",
        app_secret: str = "test_app_secret",
        base_url: str = "https://open.douyin.com",
    ):
        super().__init__(mode)
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = base_url
        self.access_token: Optional[str] = None

    def _generate_sign(self, params: Dict[str, str]) -> str:
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "".join([f"{k}{v}" for k, v in sorted_params])
        sign_str = self.app_secret + sign_str + self.app_secret
        return hashlib.md5(sign_str.encode()).hexdigest()

    def _validate_signature(self, params: Dict[str, str]) -> bool:
        if "sign" not in params:
            return False
        received_sign = params["sign"]
        calculated_sign = self._generate_sign({k: v for k, v in params.items() if k != "sign"})
        return received_sign == calculated_sign

    def get_order(self, order_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_order(order_id)
        return self._real_get_order(order_id)

    def _mock_get_order(self, order_id: str) -> Dict[str, Any]:
        return {
            "order_id": order_id,
            "status": "shipped",
            "total_amount": "99.99",
            "pay_amount": "99.99",
            "freight": "0.00",
            "receiver": {
                "name": "李四",
                "phone": "139****9000",
                "address": "上海市浦东新区",
            },
            "products": [
                {
                    "product_id": "PROD_001",
                    "name": "抖音特卖商品",
                    "price": "99.99",
                    "num": 1,
                }
            ],
            "create_time": "2026-03-01 10:00:00",
            "update_time": "2026-03-29 12:00:00",
        }

    async def _real_get_order(self, order_id: str) -> Dict[str, Any]:
        timestamp = str(int(time.time()))
        params = {
            "app_key": self.app_key,
            "method": "order.detail",
            "order_id": order_id,
            "timestamp": timestamp,
        }
        params["sign"] = self._generate_sign(params)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/order/detail", params=params)
            return response.json()

    def list_orders(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_list_orders(page, page_size)
        return self._real_list_orders(page, page_size)

    def _mock_list_orders(self, page: int, page_size: int) -> Dict[str, Any]:
        return {
            "order_list": [
                {
                    "order_id": f"DS_ORDER_{page}_{i}",
                    "status": "shipped",
                    "total_amount": "99.99",
                }
                for i in range(page_size)
            ],
            "total_count": 100,
            "page": page,
            "page_size": page_size,
        }

    def get_shipment(self, order_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_shipment(order_id)
        return self._real_get_shipment(order_id)

    def _mock_get_shipment(self, order_id: str) -> Dict[str, Any]:
        return {
            "order_id": order_id,
            "shipment_id": f"Ship_{order_id}",
            "status": "in_transit",
            "company": "中通快递",
            "tracking_no": "ZTO1234567890",
            "nodes": [
                {
                    "node": "已揽收",
                    "time": "2026-03-15 14:00:00",
                    "description": "快件已被揽收",
                },
                {
                    "node": "运输中",
                    "time": "2026-03-16 08:00:00",
                    "description": "快件正在运输途中",
                },
            ],
        }

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_refund(refund_id)
        return self._real_get_refund(refund_id)

    def _mock_get_refund(self, refund_id: str) -> Dict[str, Any]:
        return {
            "refund_id": refund_id,
            "order_id": "DS_ORDER_001",
            "status": "approved",
            "refund_amount": "99.99",
            "reason": "商品损坏",
            "apply_time": "2026-03-20 10:00:00",
            "update_time": "2026-03-29 12:00:00",
        }

    def create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_create_refund(order_id, reason, amount)
        return self._real_create_refund(order_id, reason, amount)

    def _mock_create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        return {
            "refund_id": f"DS_REF_{order_id}",
            "order_id": order_id,
            "status": "applied",
            "refund_amount": amount,
            "reason": reason,
            "apply_time": "2026-03-29 12:00:00",
        }

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Douyin Shop does not support conversation API")

    def list_messages(self, conversation_id: str, limit: int = 100) -> Dict[str, Any]:
        raise NotImplementedError("Douyin Shop does not support message API")
