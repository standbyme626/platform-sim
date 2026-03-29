from typing import Dict, Any, List, Optional
from enum import Enum


class JdOrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    WAIT_SELLER_DELIVERY = "wait_seller_delivery"
    WAIT_BUYER_RECEIVE = "wait_buyer_receive"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    REFUNDING = "refunding"
    REFUNDED = "refunded"


class JdShipmentStatus(str, Enum):
    CREATED = "created"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    SIGNED = "signed"


class JdRefundStatus(str, Enum):
    NO_REFUND = "no_refund"
    APPLIED = "applied"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDING = "refunding"
    REFUNDED = "refunded"


JD_ORDER_STATUS_TRANSITIONS: Dict[JdOrderStatus, List[JdOrderStatus]] = {
    JdOrderStatus.CREATED: [JdOrderStatus.PAID, JdOrderStatus.CANCELLED],
    JdOrderStatus.PAID: [JdOrderStatus.WAIT_SELLER_DELIVERY, JdOrderStatus.REFUNDING],
    JdOrderStatus.WAIT_SELLER_DELIVERY: [JdOrderStatus.WAIT_BUYER_RECEIVE, JdOrderStatus.REFUNDING],
    JdOrderStatus.WAIT_BUYER_RECEIVE: [JdOrderStatus.FINISHED, JdOrderStatus.REFUNDING],
    JdOrderStatus.FINISHED: [JdOrderStatus.REFUNDING],
    JdOrderStatus.CANCELLED: [],
    JdOrderStatus.REFUNDING: [JdOrderStatus.REFUNDED, JdOrderStatus.CANCELLED],
    JdOrderStatus.REFUNDED: [],
}


ORDER_SCENARIOS = {
    "basic_order": {
        "initial_order_status": JdOrderStatus.CREATED,
        "steps": [
            {"action": "pay", "next_status": JdOrderStatus.PAID},
        ],
    },
    "full_flow": {
        "initial_order_status": JdOrderStatus.CREATED,
        "steps": [
            {"action": "pay", "next_status": JdOrderStatus.PAID},
            {"action": "ship", "next_status": JdOrderStatus.WAIT_BUYER_RECEIVE},
            {"action": "receive", "next_status": JdOrderStatus.FINISHED},
        ],
    },
    "refund_flow": {
        "initial_order_status": JdOrderStatus.PAID,
        "steps": [
            {"action": "apply_refund", "next_status": JdOrderStatus.REFUNDING},
            {"action": "approve_refund", "next_status": JdOrderStatus.REFUNDED},
        ],
    },
}


SHIPMENT_SCENARIOS = {
    "basic_shipment": {
        "initial_shipment_status": JdShipmentStatus.CREATED,
        "steps": [
            {"action": "ship", "next_status": JdShipmentStatus.SHIPPED},
            {"action": "in_transit", "next_status": JdShipmentStatus.IN_TRANSIT},
            {"action": "deliver", "next_status": JdShipmentStatus.DELIVERED},
            {"action": "sign", "next_status": JdShipmentStatus.SIGNED},
        ],
    },
}


def validate_status_transition(current: JdOrderStatus, next_status: JdOrderStatus) -> bool:
    allowed = JD_ORDER_STATUS_TRANSITIONS.get(current, [])
    return next_status in allowed


def get_default_order_payload(order_id: str, status: JdOrderStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "status": status.value,
        "total_amount": "99.99",
        "pay_amount": "99.99",
        "freight": "0.00",
        "receiver": {
            "name": "王五",
            "phone": "13700137000",
            "address": "北京市朝阳区",
        },
        "vender_id": "JD_VENDER_001",
        "order_type": "B2C",
        "created_at": "2026-03-01T10:00:00+08:00",
        "updated_at": "2026-03-29T12:00:00+08:00",
    }


def get_default_shipment_payload(order_id: str, shipment_id: str, status: JdShipmentStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "shipment_id": shipment_id,
        "status": status.value,
        "logistics_company": "京东物流",
        "tracking_no": "JD1234567890",
        "shipped_at": "2026-03-15T14:00:00+08:00",
        "delivered_at": None,
        "nodes": [
            {
                "node": "已发货",
                "time": "2026-03-15T14:00:00+08:00",
                "description": "包裹已从京东仓库发出",
            },
            {
                "node": "运输中",
                "time": "2026-03-16T08:00:00+08:00",
                "description": "包裹正在运输途中",
            },
            {
                "node": "派送中",
                "time": "2026-03-17T10:00:00+08:00",
                "description": "快递员正在派送",
            },
        ],
    }


def get_default_refund_payload(order_id: str, refund_id: str, status: JdRefundStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "refund_id": refund_id,
        "status": status.value,
        "refund_amount": "50.00",
        "reason": "七天无理由退货",
        "apply_time": "2026-03-20T10:00:00+08:00",
        "update_time": "2026-03-29T12:00:00+08:00",
    }


def get_default_push_payload(event_type: str, order_id: str) -> Dict[str, Any]:
    push_templates = {
        "order_status_changed": {
            "event_type": "order_status_changed",
            "order_id": order_id,
            "old_status": "paid",
            "new_status": "wait_seller_delivery",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
        "shipment_status_changed": {
            "event_type": "shipment_status_changed",
            "order_id": order_id,
            "old_status": "shipped",
            "new_status": "in_transit",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
        "refund_applied": {
            "event_type": "refund_applied",
            "order_id": order_id,
            "refund_id": "REFUND_JD_001",
            "refund_amount": "50.00",
            "reason": "七天无理由退货",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
    }
    return push_templates.get(event_type, {"event_type": event_type, "order_id": order_id})
