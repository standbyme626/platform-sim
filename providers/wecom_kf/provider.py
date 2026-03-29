from typing import Dict, Any, Optional, List
import httpx
from providers.base.provider import BaseProvider, ProviderMode


class WecomKfProvider(BaseProvider):
    def __init__(
        self,
        mode: ProviderMode = ProviderMode.MOCK,
        corp_id: str = "test_corp_id",
        corp_secret: str = "test_corp_secret",
        base_url: str = "https://qyapi.weixin.qq.com",
    ):
        super().__init__(mode)
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.base_url = base_url
        self.access_token: Optional[str] = None

    def get_order(self, order_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Wecom KF does not support order API")

    def list_orders(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        raise NotImplementedError("Wecom KF does not support order API")

    def get_shipment(self, order_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Wecom KF does not support shipment API")

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        raise NotImplementedError("Wecom KF does not support refund API")

    def create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        raise NotImplementedError("Wecom KF does not support refund API")

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_get_conversation(conversation_id)
        return self._real_get_conversation(conversation_id)

    def _mock_get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "status": "in_session",
            "openid": "user_openid_001",
            "scene": "wework",
            "created_at": "2026-03-29 10:00:00",
            "updated_at": "2026-03-29 12:00:00",
        }

    async def _real_get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        params = {"conversation_id": conversation_id, "access_token": self.access_token}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/cgi-bin/kf/conversation/get", params=params)
            return response.json()

    def list_messages(self, conversation_id: str, limit: int = 100) -> Dict[str, Any]:
        if self.is_mock():
            return self._mock_list_messages(conversation_id, limit)
        return self._real_list_messages(conversation_id, limit)

    def _mock_list_messages(self, conversation_id: str, limit: int) -> Dict[str, Any]:
        return {
            "msg_list": [
                {
                    "msgid": f"MSG_{conversation_id}_{i}",
                    "openid": "user_openid_001",
                    "action": "send",
                    "msgtype": "text",
                    "content": "您好，请问有什么可以帮助您的？",
                    "create_time": "1743235200",
                }
                for i in range(min(limit, 10))
            ],
            "total": 100,
        }

    async def _real_list_messages(self, conversation_id: str, limit: int) -> Dict[str, Any]:
        params = {
            "conversation_id": conversation_id,
            "limit": limit,
            "access_token": self.access_token,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/cgi-bin/kf/msg_list", params=params)
            return response.json()
