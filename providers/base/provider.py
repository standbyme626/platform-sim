from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class ProviderMode(str, Enum):
    MOCK = "mock"
    REAL = "real"


class BaseProvider(ABC):
    def __init__(self, mode: ProviderMode = ProviderMode.MOCK):
        self.mode = mode

    @abstractmethod
    def get_order(self, order_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_orders(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_shipment(self, order_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_refund(self, order_id: str, reason: str, amount: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_messages(self, conversation_id: str, limit: int = 100) -> Dict[str, Any]:
        pass

    def is_mock(self) -> bool:
        return self.mode == ProviderMode.MOCK

    def is_real(self) -> bool:
        return self.mode == ProviderMode.REAL

    def switch_mode(self, mode: ProviderMode) -> None:
        self.mode = mode
