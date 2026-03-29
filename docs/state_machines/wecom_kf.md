# Wecom KF State Machine

## 1. 会话状态机

### 1.1 状态枚举

| 状态值 | 含义 | 说明 |
|--------|------|------|
| `pending` | 待接入 | 用户发起咨询，等待客服接入 |
| `in_session` | 会话中 | 客服与用户正在会话 |
| `closed` | 已关闭 | 会话正常结束 |
| `expired` | 已过期 | 会话超时自动关闭 |

### 1.2 状态转移图

```
┌──────────┐   start_session    ┌────────────┐
│ pending  │──────────────────→│ in_session │
└──────────┘                    └────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                         │
                    │ close_session           │ expire_session
                    ▼                         ▼
            ┌──────────┐               ┌──────────┐
            │  closed  │               │ expired  │
            └──────────┘               └──────────┘
```

### 1.3 转移规则

| 当前状态 | 允许转移目标 | 触发动作 |
|----------|--------------|----------|
| `pending` | `in_session` | start_session |
| `in_session` | `closed`, `expired` | close_session, expire_session |
| `closed` | (无) | - |
| `expired` | (无) | - |

---

## 2. 消息链路

### 2.1 链路流程

```
用户发送消息
    │
    ▼
Callback 通知 ───────────────────────────────────┐
    │                                                │
    ▼                                                │
同步拉取消息 (sync_msg)                              │
    │                                                │
    ▼                                                │
构建事件消息 (event_message)                         │
    │                                                │
    ▼                                                │
发送消息事件 (send_msg_on_event) ────────────────────┘
```

### 2.2 消息类型

| 消息类型 | 说明 |
|----------|------|
| `text` | 文本消息 |
| `image` | 图片消息 |
| `voice` | 语音消息 |
| `video` | 视频消息 |
| `file` | 文件消息 |
| `link` | 链接消息 |
| `miniprogram` | 小程序消息 |

---

## 3. 场景定义

### 3.1 CONVERSATION_SCENARIOS

```python
CONVERSATION_SCENARIOS = {
    "basic_session": {
        "initial_status": "pending",
        "steps": [
            {"action": "start_session", "next_status": "in_session"},
        ],
    },
    "full_session": {
        "initial_status": "pending",
        "steps": [
            {"action": "start_session", "next_status": "in_session"},
            {"action": "close_session", "next_status": "closed"},
        ],
    },
    "session_expired": {
        "initial_status": "in_session",
        "steps": [
            {"action": "expire_session", "next_status": "expired"},
        ],
    },
}
```

---

## 4. Callback 机制

### 4.1 Callback 事件类型

| 事件类型 | 说明 |
|----------|------|
| `enter_session` | 用户进入会话 |
| `leave_session` | 用户离开会话 |
| `message` | 客户发送消息 |

### 4.2 Callback Payload

```json
{
    "msg_type": "event",
    "event": "enter_session",
    "open_id": "user_open_id",
    "scene": "wework",
    "session_from": "customer_service",
    "code": "MSG_CODE_001",
    "token": "wecom_callback_token_12345",
    "timestamp": "1743235200"
}
```

---

## 5. 工件类型

| artifact_type | 说明 | 触发场景 |
|---------------|------|----------|
| `callback_payload` | 回调载荷 | callback 通知时 |
| `sync_msg_page` | 同步消息分页 | sync_msg 调用时 |
| `event_message` | 事件消息 | send_msg_on_event 时 |
| `conversation_snapshot` | 会话快照 | 会话状态变更时 |

---

## 6. 错误注入

| 错误码 | 触发条件 | 响应 |
|--------|----------|------|
| `access_token_invalid` | access_token 无效或过期 | HTTP 401 |
| `msg_code_expired` | msg_code 已过期 | HTTP 400 |
| `conversation_closed` | 会话已关闭，无法发送消息 | HTTP 400 |
| `invalid_cursor` | 无效的游标 | HTTP 400 |

---

## 7. Unified 映射

| Wecom 字段 | Unified 对象 | Unified 字段 |
|------------|--------------|--------------|
| `msgid` | Message | messageId |
| `scene` | Conversation | scene |
| `action` | Message | actionType |
| `openid` | Customer | openId |
