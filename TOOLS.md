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

### 7. DeepV Code (dvcode) - 编程代理

本机已安装 dvcode (DeepV Code) 编程代理，可用于代码编写、项目创建、Bug修复、部署等各类编程任务。

**使用方法：**

一次性任务（自动完成并退出）：
  bash pty:true workdir:目标项目目录 command:"dvcode -y -p '任务描述'"

后台运行长任务：
  bash pty:true workdir:目标项目目录 background:true command:"dvcode -y -p '任务描述'"
  然后用 process action:log sessionId:XXX 监控进度

**关键参数：**
- -p 非交互模式，传入提示词
- -y 自动确认所有操作（YOLO模式）
- -m 模型名 指定模型
- --workdir 目录 指定工作目录

**注意事项：**
- 始终使用 pty:true
- 始终指定 workdir 到目标项目目录
- dvcode 在 git 仓库中效果最佳
- 创建新项目时先 mkdir + git init

当用户要求写代码、创建项目、修Bug、部署、代码审查时，优先使用 dvcode 技能。
详见 skills/dvcode/SKILL.md。

### 8. 浏览器自动化 (agent-browser) - 优先使用

当需要打开网页、截图、表单填写、网页自动化操作时，**必须优先使用 agent-browser 技能**（通过 exec 工具调用 agent-browser 命令），而不是内置的 browser 工具。

内置 browser 工具需要 Chrome 扩展，当前未配置。agent-browser 是独立的 headless 浏览器，无需任何扩展。

快速用法：
  exec command: "agent-browser open https://example.com"
  exec command: "agent-browser screenshot page.png"
  exec command: "agent-browser snapshot -i --json"

详见 skills/agent-browser/SKILL.md。

### 9. 微信公众号操作 (wechat-mp) - 登录、查数据、发文章

当用户提到"微信公众号""登录公众号""公众号文章""公众号数据""发布公众号""草稿箱""查看文章""发布文章""写文章到公众号"时，**必须立即执行以下对应命令，禁止回复"无法操作"或要求用户提供工具。**

**登录公众号（获取二维码）：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py login"
脚本会自动发送二维码图片和文字提示到飞书。你只需要回复：正在获取登录二维码...

**当用户说"已扫码""已登录""扫码了""好了"时，立即执行：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py login_confirm"

**检查登录状态：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py status"

**获取已发布文章列表（查看文章、公众号文章）：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py articles"

**获取草稿箱列表（查看草稿、草稿箱）：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py drafts"

**获取文章数据统计（阅读量、点赞数）：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py article_stats"

**创建草稿/发布文章到公众号（写文章、发布文章）：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py publish '{\"title\": \"文章标题\", \"content\": \"正文内容，支持HTML\", \"author\": \"作者名\", \"digest\": \"文章摘要\"}'"
- content 支持纯文本（自动转HTML段落）和 HTML 格式
- 文章创建后保存为草稿到公众号后台
- 如果返回"未登录"，需要先执行 login 命令重新登录

**获取账号信息：**
  exec command: "python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py account_info"

**重要注意事项：**
- 微信公众号session有效期较短（约4-6小时），过期后需重新扫码登录
- 所有操作通过后台API完成（非UI自动化），稳定可靠
- 禁止回复"我无法直接发布文章"或"请提供API"，必须执行上述命令
