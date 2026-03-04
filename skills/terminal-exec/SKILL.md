---
name: 终端命令执行
description: 在本机终端执行shell命令。当用户要求执行命令、运行脚本、查看系统状态、安装软件、Git操作时使用。
metadata: {"clawdbot":{"emoji":"terminal","os":["darwin","linux"]}}
---

# 终端命令执行指南

你已经拥有 exec 工具，可以直接在本机执行 shell 命令。

## 使用方法

使用内置的 exec 工具：exec command: "要执行的命令"

常用参数：
- command: shell 命令（必填）
- workdir: 工作目录
- timeout: 超时秒数（默认30）
- background: 后台运行（默认false）

## 常见场景

系统信息：uname -a / sw_vers / df -h / top -l 1
文件操作：ls -la / find / cat / wc -l
Git：git status / git log --oneline -10 / git add . && git commit
包管理：brew install / npm install / pip install
网络：curl -s URL / lsof -i :端口
clawdhub 技能市场：clawdhub search 关键词 / clawdhub install 技能名
长任务：exec command: "node server.js" background: true
macOS 专属：open 文件 / pbcopy / pbpaste / say 文本

## 安全原则

1. 破坏性命令（rm -rf、dd）先确认
2. 优先 trash 代替 rm
3. 不明文输出密码密钥
4. 后台进程记录 PID
