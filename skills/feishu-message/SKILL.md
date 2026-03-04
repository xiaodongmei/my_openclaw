---
name: 飞书消息发送
description: 通过飞书发送消息给同事或群组。当用户要求发飞书消息、通知同事、群发消息、飞书沟通时使用。触发词：飞书、发消息、通知、lark。
metadata: {"clawdbot":{"emoji":"feishu","requires":{"config":["channels.feishu"]}}}
---

# 飞书消息发送指南

你已连接飞书应用（appId: cli_a92abc6e2e395cc6），可通过内置 message 工具发消息。

## 使用方法

使用内置 message 工具发飞书消息：

  message channel: "feishu" to: "目标" text: "消息内容"

## 目标格式（重要！）

飞书的 to 参数必须使用以下格式之一：

1. 群聊 ID：chat:oc_xxxxxxx
2. 用户 open_id：user:ou_xxxxxxx
3. 直接 chatId：oc_xxxxxxx

不能使用中文名字！必须使用 ID。

### 如何获取 ID

1. 在飞书开发者后台查看机器人已加入的群聊 ID
2. 通过飞书 API 获取用户 open_id
3. 通过 exec 命令调用 curl 查询：
   exec command: "curl -s -X GET 'https://open.feishu.cn/open-apis/im/v1/chats?page_size=20' -H 'Authorization: Bearer <tenant_access_token>'"

## 消息类型

### 纯文本
  message channel: "feishu" to: "chat:oc_xxx" text: "你好，这是一条测试消息"

### 富文本（Markdown）
  message channel: "feishu" to: "chat:oc_xxx" text: "**加粗** 和 *斜体*"

## 常见用法

- 发送工作通知：message channel: "feishu" to: "chat:oc_xxx" text: "任务已完成"
- 发送提醒：message channel: "feishu" to: "user:ou_xxx" text: "提醒：15分钟后有会议"
- 群发消息：对多个目标依次调用 message 工具

## 注意事项

1. 机器人需要先被添加到群聊中才能发送群消息
2. 发送私聊消息需要用户对机器人可见
3. 遵守公司通讯规范，不发送骚扰信息
4. 重要通知先确认内容再发送
