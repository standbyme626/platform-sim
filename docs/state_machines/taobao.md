# Taobao State Machine

## 1. 订单状态机

### 1.1 状态枚举

| 状态值 | 含义 | 说明 |
|--------|------|------|
| `wait_pay` | 等待付款 | 买家已下单，未付款 |
| `wait_ship` | 等待发货 | 买家已付款，等待卖家发货 |
| `shipped` | 已发货 | 卖家已发货，买家未确认收货 |
| `trade_closed` | 交易关闭 | 订单被取消或超时关闭 |
| `finished` | 交易完成 | 买家确认收货或系统自动完成 |

### 1.2 状态转移图

```
┌──────────┐      pay       ┌──────────┐
│ wait_pay │───────────────→│ wait_ship │
└──────────┘                └──────────┘
      │                          │
      │ cancel                   │ ship
      ▼                          ▼
┌──────────────┐          ┌──────────┐
│trade_closed │          │  shipped │
└──────────────┘          └──────────┘
                              │
                              │ confirm_receive
                              ▼
                        ┌──────────┐
                        │ finished │
                        └──────────┘
```

### 1.3 转移规则

| 当前状态 | 允许转移目标 | 触发动作 |
|----------|--------------|----------|
| `wait_pay` | `wait_ship`, `trade_closed` | pay, cancel |
| `wait_ship` | `shipped`, `trade_closed` | ship, cancel |
| `shipped` | `finished`, `trade_closed` | confirm_receive, cancel |
| `trade_closed` | (无) | - |
| `finished` | (无) | - |

---

## 2. 退款状态机

### 2.1 状态枚举

| 状态值 | 含义 | 说明 |
|--------|------|------|
| `no_refund` | 无退款 | 正常交易，无退款 |
| `refunding` | 退款中 | 买家申请退款，卖家处理中 |
| `refund_success` | 退款成功 | 退款完成 |
| `refund_closed` | 退款关闭 | 退款被拒绝或取消 |

### 2.2 状态转移图

```
┌───────────┐   apply_refund    ┌────────────┐
│ no_refund │────────────────→│ refunding  │
└───────────┘                  └────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │ approve                      │ reject
                    ▼                               ▼
          ┌────────────────┐              ┌──────────────┐
          │ refund_success │              │refund_closed │
          └────────────────┘              └──────────────┘
```

### 2.3 转移规则

| 当前状态 | 允许转移目标 | 触发动作 |
|----------|--------------|----------|
| `no_refund` | `refunding` | apply_refund |
| `refunding` | `refund_success`, `refund_closed` | approve, reject |
| `refund_success` | (无) | - |
| `refund_closed` | (无) | - |

---

## 3. 场景定义

### 3.1 ORDER_SCENARIOS

```python
ORDER_SCENARIOS = {
    "wait_ship_basic": {
        "initial_order_status": "wait_pay",
        "steps": [{"action": "pay", "next_status": "wait_ship"}],
    },
    "wait_ship_to_shipped": {
        "initial_order_status": "wait_ship",
        "steps": [{"action": "ship", "next_status": "shipped"}],
    },
    "shipped_to_finished": {
        "initial_order_status": "shipped",
        "steps": [{"action": "confirm_receive", "next_status": "finished"}],
    },
    "full_flow": {
        "initial_order_status": "wait_pay",
        "steps": [
            {"action": "pay", "next_status": "wait_ship"},
            {"action": "ship", "next_status": "shipped"},
            {"action": "confirm_receive", "next_status": "finished"},
        ],
    },
}
```

---

## 4. 工件类型

| artifact_type | 说明 | 触发场景 |
|---------------|------|----------|
| `trade_detail` | 交易详情 | 任意订单状态查询 |
| `order_detail` | 订单详情 | 任意订单状态查询 |
| `shipment_snapshot` | 发货快照 | 发货后 |
| `refund_snapshot` | 退款快照 | 退款申请后 |
| `push_trade_status_changed` | 状态变更推送 | 状态转移时 |

---

## 5. 错误注入

| 错误码 | 触发条件 | 响应 |
|--------|----------|------|
| `token_expired` | access_token 过期 | HTTP 401 |
| `resource_not_found` | 订单不存在 | HTTP 404 |
| `duplicate_push` | 重复推送 | HTTP 200 + warning |
| `out_of_order_push` | 乱序推送 | HTTP 200 + warning |
| `rate_limited` | 调用频率超限 | HTTP 429 |

---

## 6. Unified 映射

| Taobao 字段 | Unified 对象 | Unified 字段 |
|-------------|--------------|--------------|
| `trade.tid` | Order | orderId |
| `order.oid` | OrderItem | itemOrderId / extra.subOrderId |
| `trade.status` | Order | status |
| `orders[].status` | OrderItem | itemStatus |
| `refund/rights state` | AfterSale | status |
