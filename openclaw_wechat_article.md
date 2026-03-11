# 如何让OpenClaw发表公众号

使用OpenClaw助手，可以轻松实现自动发表微信公众号文章。以下是一步步的指南，帮助你快速上手。

## 设置OpenClaw
1. **安装OpenClaw：** 确保你已经在本地成功安装OpenClaw。
2. **配置技能：** 添加微信公众平台相关的技能，确保可以通过OpenClaw进行登录和文章发布。
3. **登录账号：** 使用提供的命令脚本登录公众号。

```bash
python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py login
```

## 准备文章草稿
在撰写和编辑文章时，可以使用Markdown格式来便于排版。

```markdown
# 标题

## 小标题

- 列表项
- 列表项

文章内容
```

## 发布文章
当草稿准备好后，可以通过以下命令直接发布：

```bash
python3 ~/.openclaw/workspace/skills/wechat-mp/wechat_mp_client.py publish '{"title": "如何让OpenClaw发表公众号", "content": "这是关于使用OpenClaw助手发表微信公众号文章的指南。", "author": "OpenClaw"}'
```

## 注意事项
- 确保OpenClaw的配置文件中包含正确的微信公众号API接口信息。
- 在发布前，检查文章的内容和格式。

通过以上步骤，你就可以轻松实现通过OpenClaw助手自动发表微信公众号文章。希望这篇指南能帮助到你！