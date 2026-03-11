# Long-term Memory

## Key Facts

- Platform: macOS (darwin)
- OpenClaw version: 0.1.6 (openclaw-cn)
- Primary model: openai/gpt-4o
- Feishu channel: enabled (appId: cli_a92abc6e2e395cc6)
- Skills: xiaohongshu-engage, xiaohongshu-trending, xiaohongshu-mcp, anycrawl, terminal-exec, feishu-message, clawdhub-search, dvcode-image

## Lessons Learned

- Feishu message tool requires ID format (chat:oc_xxx or user:ou_xxx), NOT Chinese names
- dvcode-image 生图：绝对禁止直接用 dvcode 命令（会进 pty 模式挂起）。必须用 python3 ~/.openclaw/skills/dvcode-image/dvcode_image.py，设置 timeout:120，同步等待结果，不允许中途回复"正在进行中"
- 长耗时命令（>10秒）必须设置足够的 timeout，不能让 agent 提前放弃
