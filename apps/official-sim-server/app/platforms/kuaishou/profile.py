from typing import Dict, Any, List, Optional
from enum import Enum


class KuaishouOrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    WAIT_DELIVERY = "wait_delivery"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    REFUND_APPLIED = "refund_applied"
    REFUND_PROCESSING = "refund_processing"
    REFUND_SUCCESS = "refund_success"
    REFUND_REJECTED = "refund_rejected"


class KuaishouLogisticsStatus(str, Enum):
    CREATED = "created"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    SIGNED = "signed"


class KuaishouRefundStatus(str, Enum):
    NO_REFUND = "no_refund"
    APPLIED = "applied"
    PROCESSING = "processing"
    SUCCESS = "success"
    REJECTED = "rejected"


KUAISHOU_ORDER_STATUS_TRANSITIONS: Dict[KuaishouOrderStatus, List[KuaishouOrderStatus]] = {
    KuaishouOrderStatus.CREATED: [KuaishouOrderStatus.PAID, KuaishouOrderStatus.CANCELLED],
    KuaishouOrderStatus.PAID: [KuaishouOrderStatus.WAIT_DELIVERY, KuaishouOrderStatus.REFUND_APPLIED],
    KuaishouOrderStatus.WAIT_DELIVERY: [KuaishouOrderStatus.DELIVERED, KuaishouOrderStatus.REFUND_APPLIED],
    KuaishouOrderStatus.DELIVERED: [KuaishouOrderStatus.CONFIRMED, KuaishouOrderStatus.REFUND_APPLIED],
    KuaishouOrderStatus.CONFIRMED: [KuaishouOrderStatus.FINISHED, KuaishouOrderStatus.REFUND_APPLIED],
    KuaishouOrderStatus.FINISHED: [KuaishouOrderStatus.REFUND_APPLIED],
    KuaishouOrderStatus.CANCELLED: [],
    KuaishouOrderStatus.REFUND_APPLIED: [KuaishouOrderStatus.REFUND_PROCESSING, KuaishouOrderStatus.REFUND_REJECTED],
    KuaishouOrderStatus.REFUND_PROCESSING: [KuaishouOrderStatus.REFUND_SUCCESS],
    KuaishouOrderStatus.REFUND_SUCCESS: [],
    KuaishouOrderStatus.REFUND_REJECTED: [],
}


ORDER_SCENARIOS = {
    "basic_order": {
        "initial_order_status": KuaishouOrderStatus.CREATED,
        "steps": [
            {"action": "pay", "next_status": KuaishouOrderStatus.PAID},
        ],
    },
    "full_flow": {
        "initial_order_status": KuaishouOrderStatus.CREATED,
        "steps": [
            {"action": "pay", "next_status": KuaishouOrderStatus.PAID},
            {"action": "deliver", "next_status": KuaishouOrderStatus.DELIVERED},
            {"action": "confirm", "next_status": KuaishouOrderStatus.CONFIRMED},
            {"action": "finish", "next_status": KuaishouOrderStatus.FINISHED},
        ],
    },
    "refund_flow": {
        "initial_order_status": KuaishouOrderStatus.PAID,
        "steps": [
            {"action": "apply_refund", "next_status": KuaishouOrderStatus.REFUND_APPLIED},
            {"action": "process_refund", "next_status": KuaishouOrderStatus.REFUND_PROCESSING},
            {"action": "refund_success", "next_status": KuaishouOrderStatus.REFUND_SUCCESS},
        ],
    },
}


LOGISTICS_SCENARIOS = {
    "basic_logistics": {
        "initial_status": KuaishouLogisticsStatus.CREATED,
        "steps": [
            {"action": "pick_up", "next_status": KuaishouLogisticsStatus.PICKED_UP},
            {"action": "in_transit", "next_status": KuaishouLogisticsStatus.IN_TRANSIT},
            {"action": "out_for_delivery", "next_status": KuaishouLogisticsStatus.OUT_FOR_DELIVERY},
            {"action": "sign", "next_status": KuaishouLogisticsStatus.SIGNED},
        ],
    },
}


def validate_status_transition(current: KuaishouOrderStatus, next_status: KuaishouOrderStatus) -> bool:
    allowed = KUAISHOU_ORDER_STATUS_TRANSITIONS.get(current, [])
    return next_status in allowed


def get_default_order_payload(order_id: str, status: KuaishouOrderStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "status": status.value,
        "total_amount": "99.99",
        "pay_amount": "99.99",
        "freight": "0.00",
        "product_count": 1,
        "receiver": {
            "name": "孙七",
            "phone": "13500135000",
            "address": "深圳市南山区",
        },
        "shop_name": "快手小店",
        "order_type": "KS_ORDER",
        "created_at": "2026-03-01T10:00:00+08:00",
        "updated_at": "2026-03-29T12:00:00+08:00",
    }


def get_default_product_payload(product_id: str) -> Dict[str, Any]:
    return {
        "product_id": product_id,
        "product_name": "快手特卖商品",
        "price": "99.99",
        "stock": 100,
        "status": "on_sale",
    }


def get_default_logistics_payload(order_id: str, logistics_id: str, status: KuaishouLogisticsStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "logistics_id": logistics_id,
        "status": status.value,
        "company": "快手物流",
        "tracking_no": "KS1234567890",
        "nodes": [
            {
                "node": "已揽收",
                "time": "2026-03-15T14:00:00+08:00",
                "description": "商品已被快递员揽收",
            },
            {
                "node": "运输中",
                "time": "2026-03-16T08:00:00+08:00",
                "description": "商品正在运输途中",
            },
            {
                "node": "派送中",
                "time": "2026-03-17T10:00:00+08:00",
                "description": "快递员正在派送",
            },
        ],
    }


def get_default_refund_payload(order_id: str, refund_id: str, status: KuaishouRefundStatus) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "refund_id": refund_id,
        "status": status.value,
        "refund_amount": "99.99",
        "reason": "商品损坏",
        "apply_time": "2026-03-20T10:00:00+08:00",
        "update_time": "2026-03-29T12:00:00+08:00",
    }


def get_default_push_payload(event_type: str, order_id: str) -> Dict[str, Any]:
    push_templates = {
        "order_status_changed": {
            "event_type": "order_status_changed",
            "order_id": order_id,
            "old_status": "paid",
            "new_status": "wait_delivery",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
        "logistics_changed": {
            "event_type": "logistics_changed",
            "order_id": order_id,
            "old_status": "picked_up",
            "new_status": "in_transit",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
        "refund_applied": {
            "event_type": "refund_applied",
            "order_id": order_id,
            "refund_id": "REFUND_KS_001",
            "refund_amount": "99.99",
            "reason": "商品损坏",
            "timestamp": "2026-03-29T12:00:00+08:00",
        },
    }
    return push_templates.get(event_type, {"event_type": event_type, "order_id": order_id})
