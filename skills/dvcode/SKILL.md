---
name: DeepV Code
description: 通过 dvcode CLI 调用 DeepV Code 智能编程代理，实现代码编写、项目部署、文件操作、代码审查等各类软件工程任务。
metadata: {"clawdbot":{"emoji":"🧑‍💻","requires":{"anyBins":["dvcode"]}}}
---

# DeepV Code (dvcode) 编程代理

使用 **dvcode** CLI 在指定项目目录中执行编程任务。dvcode 是一个强大的 AI 编程助手，支持代码编写、调试、部署、文件操作等。

## 安装位置

```
可执行文件: /opt/homebrew/bin/dvcode
版本: 1.0.307
```

## 基本用法

### 一次性任务（非交互模式）

使用 `-p` 参数传入提示词，dvcode 会自动完成任务并退出：

```bash
# 在指定项目目录执行编程任务
bash pty:true workdir:~/Projects/myproject command:"dvcode -p '你的任务描述'"

# YOLO 模式（自动确认所有操作，无需审批）
bash pty:true workdir:~/Projects/myproject command:"dvcode -y -p '创建一个 Express REST API'"

# 指定模型
bash pty:true workdir:~/Projects/myproject command:"dvcode -m claude-opus-4-6 -p '重构认证模块'"
```

### 后台运行（长任务）

对于耗时较长的任务，使用后台模式：

```bash
# 后台启动
bash pty:true workdir:~/Projects/myproject background:true command:"dvcode -y -p '构建完整的用户管理系统'"

# 监控进度
process action:log sessionId:XXX

# 检查是否完成
process action:poll sessionId:XXX

# 终止
process action:kill sessionId:XXX
```

## 常见任务模板

### 创建新项目

```bash
bash pty:true workdir:~/Projects command:"mkdir -p newproject && cd newproject && git init && dvcode -y -p '初始化一个 Next.js 项目，配置 TypeScript、Tailwind CSS 和 ESLint'"
```

### 代码编写

```bash
bash pty:true workdir:~/Projects/myproject command:"dvcode -y -p '在 src/api/ 下创建用户 CRUD API，使用 Express + Prisma'"
```

### Bug 修复

```bash
bash pty:true workdir:~/Projects/myproject command:"dvcode -y -p '修复 src/auth/login.ts 中的认证逻辑 bug'"
```

### 代码审查

```bash
bash pty:true workdir:~/Projects/myproject command:"dvcode -p '审查 src/ 目录下的代码，找出潜在问题'"
```

### 部署配置

```bash
bash pty:true workdir:~/Projects/myproject command:"dvcode -y -p '创建 Dockerfile 和 docker-compose.yml'"
```

### 测试编写

```bash
bash pty:true workdir:~/Projects/myproject command:"dvcode -y -p '为 src/services/ 编写单元测试，使用 Jest'"
```

## 关键参数

| 参数 | 说明 |
|------|------|
| `-p, --prompt` | 非交互模式，直接执行提示词任务 |
| `-y, --yolo` | 自动确认所有操作 |
| `-m, --model` | 指定 AI 模型 |
| `-s, --sandbox` | 沙箱模式运行 |
| `-c, --continue` | 继续上一次会话 |
| `--workdir` | 指定工作目录 |
| `--output-format stream-json` | 流式 JSON 输出 |

## ACP 桥接模式

dvcode 支持 ACP（Agent Control Protocol）模式，可以直接与 openclaw 网关桥接：

```bash
# 启动 dvcode 的 ACP 模式连接到 openclaw 网关
dvcode --experimental-acp --workdir ~/Projects/myproject
```

通过 openclaw 的 ACP 桥接调用：

```bash
openclaw-cn acp client --server dvcode --server-args "--experimental-acp" --cwd ~/Projects/myproject
```

## 并行任务

```bash
# 前端
bash pty:true workdir:~/Projects/frontend background:true command:"dvcode -y -p '实现用户注册页面'"
# 后端
bash pty:true workdir:~/Projects/backend background:true command:"dvcode -y -p '实现用户注册 API'"
```

## 自动通知完成

```bash
bash pty:true workdir:~/Projects/myproject background:true command:"dvcode -y -p '完成任务后运行: openclaw-cn gateway wake --text \"Done: 任务完成\" --mode now'"
```

## 注意事项

1. **始终使用 pty:true** — dvcode 是交互式终端应用
2. **workdir 很重要** — 确保在正确项目目录运行
3. **敏感操作用 -s** — 沙箱模式更安全
4. **长任务用 background** — 避免阻塞
5. **Git 仓库优先** — dvcode 在 git 仓库中效果最佳
6. **不要在 ~/.openclaw/ 中运行** — 避免干扰 openclaw 配置
