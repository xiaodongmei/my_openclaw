---
name: xiaohongshu-mcp
description: 小红书操作。登录小红书获取二维码、搜索内容、发布图文笔记、发布视频、评论点赞收藏。触发词：小红书、登录小红书、发小红书、小红书发布、小红书搜索。
metadata: {"openclaw":{"emoji":"📕","always":true}}
---

# 小红书操作

通过 MCP 服务（端口18060）+ Python脚本实现小红书自动化操作。

## 使用方法

所有操作通过 exec 工具调用 Python 脚本：

### 检查MCP服务状态
  exec command: "curl -s http://localhost:18060/mcp -o /dev/null -w '%{http_code}'"
返回405表示服务正常。如果返回000，需要启动服务：
  exec command: "nohup ~/.local/bin/xiaohongshu-mcp -port :18060 > /tmp/xhs-mcp.log 2>&1 & sleep 3 && curl -s http://localhost:18060/mcp -o /dev/null -w '%{http_code}'"

### 检查登录状态
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py status"

### 登录（获取二维码）
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py login"
会返回二维码图片保存路径。告知用户路径，等用户说"已扫码"后执行：
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py status"

### 搜索内容
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py search '关键词'"

### 获取推荐列表
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py feeds"

### 发布图文笔记
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py smart_publish '{\"title\": \"标题\", \"content\": \"正文\", \"images\": [\"/图片路径.png\"], \"auto_optimize\": true}'"
标题不超过20字，必须有至少1张图片。

### 发布视频
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py publish_video '{\"title\": \"标题\", \"content\": \"正文\", \"video\": \"/视频路径.mp4\"}'"

### 评论
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py comment '{\"feed_id\": \"帖子ID\", \"xsec_token\": \"token\", \"comment\": \"评论内容\"}'"

### 点赞
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py like '{\"feed_id\": \"帖子ID\", \"xsec_token\": \"token\"}'"

### 收藏
  exec command: "python3 ~/.openclaw/workspace/skills/xiaohongshu-mcp/mcp_client.py favorite '{\"feed_id\": \"帖子ID\", \"xsec_token\": \"token\"}'"

## 重要说明
- MCP服务必须先启动在端口18060，否则所有操作会失败
- 首次使用需要用小红书App扫码登录，登录二维码有效期约2分钟
- 发布图文必须有至少1张真实存在的图片文件
- 所有操作结果以exec命令的实际输出为准，必须如实告知用户
- 多次操作间请保持30秒以上间隔
