# Douyin Shop State Machine

## 1. 订单状态机

### 1.1 状态枚举

| 状态值 | 含义 | 说明 |
|--------|------|------|
| `created` | 已创建 | 订单创建，待付款 |
| `paid` | 已付款 | 买家已付款 |
| `shipped` | 已发货 | 卖家已发货 |
| `confirmed` | 已确认收货 | 买家确认收货 |
| `completed` | 已完成 | 订单完成 |
| `cancelled` | 已取消 | 订单取消 |
| `refunding` | 退款中 | 退款处理中 |
| `refunded` | 已退款 | 退款完成 |

### 1.2 状态转移图

```
┌──────────┐      pay       ┌────────┐
│ created  │───────────────→│  paid  │
└──────────┘                └────────┘
      │                          │
      │ cancel                   │ ship
      ▼                          ▼
┌───────────┐             ┌──────────┐
│ cancelled │             │ shipped  │
└───────────┘             └──────────┘
                              │
                              │ confirm
                              ▼
                        ┌──────────┐
                        │confirmed │
                        └──────────┘
                              │
                              │ complete
                              ▼
                        ┌──────────┐
                        │completed │
                        └──────────┘

  paid/shipped/confirmed/completed
           │
           │ apply_refund
           ▼
      ┌───────────┐      approve       ┌──────────┐
      │ refunding │──────────────────→│ refunded │
      └───────────┘                   └──────────┘
           │
           │ cancel
           ▼
      ┌───────────┐
      │ cancelled │
      └───────────┘
```

### 1.3 转移规则

| 当前状态 | 允许转移目标 | 触发动作 |
|----------|--------------|----------|
| `created` | `paid`, `cancelled` | pay, cancel |
| `paid` | `shipped`, `refunding` | ship, apply_refund |
| `shipped` | `confirmed`, `refunding` | confirm, apply_refund |
| `confirmed` | `completed`, `refunding` | complete, apply_refund |
| `completed` | `refunding` | apply_refund |
| `cancelled` | (无) | - |
| `refunding` | `refunded`, `cancelled` | approve_refund, cancel |
| `refunded` | (无) | - |

---

## 2. 退款状态机

### 2.1 状态枚举

| 状态值 | 含义 | 说明 |
|--------|------|------|
| `no_refund` | 无退款 | 正常订单 |
| `applied` | 已申请 | 买家申请退款 |
| `approved` | 已同意 | 卖家同意退款 |
| `rejected` | 已拒绝 | 卖家拒绝退款 |
| `refunding` | 退款中 | 退款处理中 |
| `refunded` | 已退款 | 退款完成 |
| `closed` | 已关闭 | 退款关闭 |

### 2.2 转移规则

| 当前状态 | 允许转移目标 | 触发动作 |
|----------|--------------|----------|
| `no_refund` | `applied` | apply |
| `applied` | `approved`, `rejected` | approve, reject |
| `approved` | `refunding` | process |
| `rejected` | `closed` | close |
| `refunding` | `refunded` | complete |
| `refunded` | (无) | - |
| `closed` | (无) | - |

---

## 3. 场景定义

### 3.1 ORDER_SCENARIOS

```python
ORDER_SCENARIOS = {
    "basic_paid_to_shipped": {
        "initial_order_status": "paid",
        "steps": [{"action": "ship", "next_status": "shipped"}],
    },
    "basic_shipped_to_confirmed": {
        "initial_order_status": "shipped",
        "steps": [{"action": "confirm", "next_status": "confirmed"}],
    },
    "basic_confirmed_to_completed": {
        "initial_order_status": "confirmed",
        "steps": [{"action": "complete", "next_status": "completed"}],
    },
    "full_flow": {
        "initial_order_status": "created",
        "steps": [
            {"action": "pay", "next_status": "paid"},
            {"action": "ship", "next_status": "shipped"},
            {"action": "confirm", "next_status": "confirmed"},
            {"action": "complete", "next_status": "completed"},
        ],
    },
    "refund_flow": {
        "initial_order_status": "paid",
        "steps": [
            {"action": "apply_refund", "next_status": "refunding"},
            {"action": "approve_refund", "next_status": "refunded"},
        ],
    },
}
```

---

## 4. 签名校验

### 4.1 校验参数

抖店 API 调用必须包含签名参数：

| 参数 | 说明 |
|------|------|
| `app_key` | 应用 Key |
| `timestamp` | 时间戳 |
| `sign` | 签名值 |
| `method` | API 方法名 |

### 4.2 签名算法

```
sign = MD5(app_secret + method + timestamp + body)
```

---

## 5. 工件类型

| artifact_type | 说明 | 触发场景 |
|---------------|------|----------|
| `order_detail` | 订单详情 | 任意订单查询 |
| `push_order_status_changed` | 状态变更推送 | 状态转移时 |
| `refund_snapshot` | 退款快照 | 退款申请后 |
| `sign_error_response` | 签名错误响应 | 签名校验失败时 |

---

## 6. 错误注入

| 错误码 | 触发条件 | 响应 |
|--------|----------|------|
| `invalid_signature` | 签名校验失败 | HTTP 401 |
| `token_expired` | access_token 过期 | HTTP 401 |
| `permission_denied` | 权限不足 | HTTP 403 |
| `duplicate_push` | 重复推送 | HTTP 200 + warning |
| `rate_limited` | 调用频率超限 | HTTP 429 |

---

## 7. Unified 映射

| Douyin 字段 | Unified 对象 | Unified 字段 |
|-------------|--------------|--------------|
| `order_id` | Order | orderId |
| `status` | Order | status |
| `refund_id` | AfterSale | afterSaleId |
| `push_event.type` | PushEvent | eventType |
