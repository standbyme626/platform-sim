from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.response import success_response
from app.adapters.registry import PlatformRegistry
from app.services.platform_gateway_service import PlatformGatewayService
from app.services.order_domain_service import OrderDomainService
from app.services.shipment_domain_service import ShipmentDomainService
from app.services.after_sale_domain_service import AfterSaleDomainService
from app.services.conversation_domain_service import ConversationDomainService
from app.services.business_context_service import BusinessContextService

router = APIRouter()


class BuildContextRequest(BaseModel):
    platform: str
    biz_id: str
    biz_type: str = "order"
    include_inventory: bool = False
    include_risk: bool = True
    include_quality: bool = True
    include_recommendations: bool = True


def get_context_service() -> BusinessContextService:
    registry = PlatformRegistry()
    gateway = PlatformGatewayService(registry)
    order_service = OrderDomainService(gateway, registry)
    shipment_service = ShipmentDomainService(gateway)
    after_sale_service = AfterSaleDomainService(gateway)
    conversation_service = ConversationDomainService(gateway)
    return BusinessContextService(
        gateway,
        order_service,
        shipment_service,
        after_sale_service,
        conversation_service,
    )


@router.get("/{platform}/{biz_id}")
async def get_context(
    platform: str,
    biz_id: str,
):
    try:
        service = get_context_service()
        context = service.get_context(platform, biz_id)
        return success_response(context)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Context not found: {biz_id}")


@router.post("/build")
async def build_context(request: BuildContextRequest):
    try:
        service = get_context_service()
        options = {
            "include_inventory": request.include_inventory,
            "include_risk": request.include_risk,
            "include_quality": request.include_quality,
            "include_recommendations": request.include_recommendations,
        }
        context = service.build_context(
            request.platform,
            request.biz_id,
            request.biz_type,
            options,
        )
        return success_response(context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh_context(request: BuildContextRequest):
    try:
        service = get_context_service()
        context = service.build_context(
            request.platform,
            request.biz_id,
            request.biz_type,
        )
        return success_response(context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
