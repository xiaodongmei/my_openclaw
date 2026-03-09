---
name: 小红书自动驾驶
description: 小红书全流程自动化：搜爆文选题→分析爆款模式→生成小红书风格帖子→发布到小红书。当用户要求做小红书选题、找爆文、自动写小红书、一键发布小红书、小红书全流程时使用。触发词：小红书选题、小红书爆文、小红书全流程、一键发小红书、小红书自动、找选题写帖子、爆文选题。
metadata: {"clawdbot":{"emoji":"rocket"}}
---

# 小红书自动驾驶 — 全流程自动化

## 严格规则

1. **禁止假执行**：所有小红书操作必须通过 exec 命令调用 mcp_client.py 脚本。不要凭空说"已发布"或"已登录"。
2. **必须检查返回结果**：每次 exec 后根据实际输出告知用户，不要编造。
3. **发布前必须确认登录**：通过 mcp_client.py status 确认已登录。
4. **发布必须有图片**：小红书必须有配图，至少1张。如果没有图片，告知用户需要准备图片。

## 脚本路径

  ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py

## 全流程概览

用户输入关键词/领域 → 搜索爆文（web_search） → 分析选题 → 生成帖子 → 用户确认 → 通过 exec 命令发布到小红书

## 搜索爆文

使用 web_search 搜索小红书爆款内容：

  web_search query: "site:xiaohongshu.com [领域关键词] 爆款"

或者通过 MCP 搜索（需要先确认登录）：

  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py search '关键词' --sort 最多点赞"

## 生成帖子

### 写作要求
- 标题不超过20个字符
- 正文300-800字
- 口语化、像跟朋友聊天
- 每段开头用emoji
- 结尾引导互动

### 帖子格式
每篇帖子输出：标题、正文、标签列表、配图建议

## 发布到小红书

发布前必须按顺序执行：

1. exec: curl -s http://localhost:18060/mcp -o /dev/null -w '%{http_code}' → 确认MCP服务运行
2. exec: python3 mcp_client.py status → 确认已登录
3. 如未登录 → exec: python3 mcp_client.py login → 展示二维码，等用户扫码
4. exec: python3 mcp_client.py smart_publish '{"title":"...","content":"...","images":["..."],"auto_optimize":true}' → 发布
5. 检查返回结果告知用户

## 注意事项

- 发布图文必须有至少1张图片
- 每天建议不超过5篇，间隔大于30分钟
- 基于爆文模式创作，不要直接搬运
- 所有操作结果以 exec 命令的实际输出为准
