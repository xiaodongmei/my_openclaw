---
name: ClawdHub 技能搜索与安装
description: 搜索和安装 ClawdHub 技能市场的 skills。当用户要求搜索技能、查找插件、安装新功能、浏览 clawdhub 市场时使用。触发词：clawdhub、搜索技能、安装技能、技能市场、skill market。
metadata: {"clawdbot":{"emoji":"search"}}
---

# ClawdHub 技能搜索与安装

通过 clawdhub CLI 命令搜索和安装社区技能。

## 搜索技能

使用 exec 工具执行 clawdhub 命令：

  exec command: "clawdhub search 关键词"

示例：
  exec command: "clawdhub search xiaohongshu"
  exec command: "clawdhub search weather"
  exec command: "clawdhub search feishu"
  exec command: "clawdhub search browser"

## 安装技能

  exec command: "clawdhub install 技能名"

## 查看已安装技能

  exec command: "ls ~/.openclaw/skills/"

或查看每个技能的详情：
  exec command: "cat ~/.openclaw/skills/技能名/SKILL.md"

## 卸载技能

  exec command: "clawdhub uninstall 技能名"

## 当前已安装的技能

- anycrawl - 网页爬取
- xiaohongshu-engage - 小红书互动评论
- xiaohongshu-trending - 小红书爆款采集
- xiaohongshu-mcp - 小红书上传工具
- terminal-exec - 终端命令执行
- feishu-message - 飞书消息发送
