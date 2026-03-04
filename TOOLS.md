# TOOLS.md - 本地环境配置与工具使用规则

## 关键规则（每次必读）

### 1. web_search 不可用 - 必须用 exec 替代

当前没有配置 Brave Search API Key，web_search 会返回 missing_brave_api_key 错误。

**遇到此错误时，必须立即使用 exec 工具通过 curl 搜索，禁止直接告诉用户无法搜索。**

搜索方法：
  exec command: "curl -sL 'https://html.duckduckgo.com/html/?q=搜索关键词' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' | grep -o 'result__a.*href=[^ ]*' | head -10"

### 2. web_fetch 失败时用 exec + curl 替代

  exec command: "curl -sL '目标URL' -H 'User-Agent: Mozilla/5.0' | head -500"

### 3. 飞书消息 - 必须使用 ID 格式

飞书 message 工具的 to 参数不能使用中文姓名，必须使用 ID。

已知联系人：
- xiaodongmei (肖冬梅/当前用户) -> user:ou_2a8de8097294e557f1d8ca5d08e91c63
- AI 助理 (机器人自身) -> user:ou_d3c085140b115ef7830bf40753af236d

如果不知道对方 ID，告诉用户需要提供手机号或 open_id。

飞书发消息权限已开通，可以正常发送消息。
群聊列表查询权限（im:chat:readonly）尚未开通，如需获取群列表可在开发者后台添加。

### 4. sessions_spawn 禁止使用

sessions_spawn 在当前配置中被禁止。不要调用它。
需要子任务时直接在当前会话用 exec 工具完成。

### 5. 小红书爆款获取方法

直接用 exec + curl 搜索小红书内容：
  exec command: "curl -sL 'https://html.duckduckgo.com/html/?q=site:xiaohongshu.com+热门+爆款' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' | grep -o 'uddg=[^ ]*' | head -20"

### 6. 金融数据获取方法

查金价等数据：
  exec command: "curl -sL 'https://html.duckduckgo.com/html/?q=gold+price+today+黄金价格' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' | grep -o 'uddg=[^ ]*' | head -10"

然后用 curl 抓取搜索结果中的页面获取实际数据。

## 环境信息

- 平台：macOS (darwin)
- OpenClaw 版本：0.1.6 (openclaw-cn)
- 飞书通道：已启用但缺少 API 权限
- 搜索引擎：Brave API Key 未配置，使用 exec+curl+DuckDuckGo 替代
