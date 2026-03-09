---
name: wechat-mp
description: 微信公众号后台操作。登录公众号获取二维码、查看已发布文章和草稿、文章数据统计（阅读量/点赞数）、创建草稿发布文章。触发词：公众号、微信公众号、登录公众号、公众号文章、发布文章、草稿箱。
metadata: {"openclaw":{"emoji":"📱","always":true}}
---

# 微信公众号操作

通过 agent-browser 浏览器 + 微信后台API 实现公众号自动化操作。

## 使用方法

所有操作通过 exec 工具调用 Python 脚本：

### 登录（获取二维码）
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py login"
二维码会自动通过飞书发送给用户。等用户说"已扫码"后执行：
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py login_confirm"

### 检查登录状态
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py status"

### 获取已发布文章列表
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py articles"

### 获取草稿箱列表
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py drafts"

### 获取文章数据统计（阅读量、点赞数）
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py article_stats"

### 创建草稿/发布文章
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py publish '{\"title\": \"标题\", \"content\": \"正文内容\", \"author\": \"作者\", \"digest\": \"摘要\"}'"
content支持HTML格式和纯文本。纯文本会自动转换为HTML段落。

### 获取账号信息
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py account_info"

## 重要说明
- 微信公众号后台session有效期较短（约4-6小时），如果操作返回"未登录"需要重新扫码
- 创建的文章保存为草稿，群发发布需要在公众号后台手动操作
- 所有API通过浏览器内fetch调用，比UI自动化更稳定
