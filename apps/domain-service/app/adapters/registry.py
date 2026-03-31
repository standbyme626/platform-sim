from typing import Dict, Any, Optional, Type
from enum import Enum

from models.unified import Platform
from app.adapters.capabilities import PlatformCapabilities, get_platform_capabilities
from app.adapters.contracts import BaseAdapter


class PlatformRegistry:
    _adapters: Dict[Platform, BaseAdapter] = {}
    _capabilities: Dict[Platform, PlatformCapabilities] = {}
    
    def register(
        self,
        platform: Platform,
        adapter: BaseAdapter,
        capabilities: Optional[PlatformCapabilities] = None,
    ):
        self._adapters[platform] = adapter
        self._capabilities[platform] = capabilities or get_platform_capabilities(platform)
    
    def get_adapter(self, platform: Platform) -> Optional[BaseAdapter]:
        return self._adapters.get(platform)
    
    def get_capabilities(self, platform: Platform) -> PlatformCapabilities:
        return self._capabilities.get(
            platform,
            get_platform_capabilities(platform)
        )
    
    def is_registered(self, platform: Platform) -> bool:
        return platform in self._adapters
    
    def list_platforms(self) -> list:
        return list(self._adapters.keys())
    
    def list_supported_platforms(self) -> list:
        return [p for p in self._adapters.keys()]
    
    def get_supported_capabilities(self, platform: Platform) -> list:
        caps = self.get_capabilities(platform)
        return [c.value for c in caps.capabilities]
