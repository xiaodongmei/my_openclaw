---
name: sanwan-ppt
description: 生成三万同款板书风格PPT。白板背景+硬笔书法字+手绘彩色插图+戴龙虾帽的拉布拉多吉祥物。触发词：三万同款、板书PPT、白板PPT、手绘PPT、生成PPT、做PPT。
metadata: {"openclaw":{"emoji":"🎨"}}
---

# 三万同款板书风格 PPT

## 风格说明

| 元素 | 描述 |
|---|---|
| 背景 | 真实白板铺满整个16:9画面，四边框完整可见 |
| 文字 | 硬笔钢笔手写书法，笔画精准流畅，有墨色变化 |
| 插图 | 手绘彩色卡通，黑色马克笔勾线+彩色马克笔上色，有层次阴影 |
| 吉祥物 | **每页必须出现**：戴红色龙虾帽的可爱拉布拉多，chibi风格 |
| 标注 | 红色/黑色手绘笔迹（箭头、下划线、✕、✓） |

---

## 工作流程

### Step 1：确认大纲
询问用户：主题、页数、每页核心内容。适合对比/步骤/介绍/总结类内容。

### Step 2：构建每页 prompt_body

每页 prompt_body 写法（**不含 STYLE 前缀，脚本自动加**）：

**文字统一用：** `elegant fountain pen Chinese calligraphy handwriting`
**插图统一用：** `hand-drawn cartoon illustration, bold black marker outline, vivid colored marker fill (Copic style), layered shadows for depth, NOT flat vector`
**吉祥物统一用：** `[MUST INCLUDE] cute chibi Labrador with red lobster-claw hat, [表情], placed at [位置]`
**强调色用：** `bold red fountain pen Chinese`

**三栏对比页示例 prompt_body：**
```
Top: large elegant fountain pen Chinese calligraphy: 页面标题
Medium fountain pen below: 副标题说明
Red hand-drawn pen underline.

Three sections side by side, separated by thin hand-drawn vertical lines:

Left section:
Hand-drawn cartoon illustration: [插图描述，vivid colors, marker-colored]
Elegant fountain pen Chinese below: 标题一
Smaller fountain pen text: 说明文字

Center section:
Hand-drawn cartoon illustration: [插图描述]
Elegant fountain pen Chinese below: 标题二
Smaller fountain pen text: 说明文字

Right section:
Hand-drawn cartoon illustration: [插图描述]
Elegant fountain pen Chinese below: 标题三
Smaller fountain pen text: 说明文字

[MUST INCLUDE] cute chibi Labrador with red lobster-claw hat, excited expression,
waving paw, placed at bottom-left corner.
Bottom center, large bold red fountain pen Chinese: 核心金句或CTA
```

---

## 调用脚本

### 生成 PPT（核心命令）

```
exec command: "cd ~/.openclaw/workspace && venv/bin/python3 skills/sanwan-ppt/scripts/generate_ppt.py '<slides_json>' /tmp/sanwan_output.pptx"
```

`slides_json` 格式：
```json
[
  {
    "title": "封面",
    "prompt_body": "Top center: large elegant fountain pen Chinese calligraphy: 标题\n[MUST INCLUDE] cute chibi Labrador with red lobster-claw hat, excited expression, placed at bottom-right."
  },
  {
    "title": "第二页",
    "prompt_body": "..."
  }
]
```

### 安装依赖（首次使用）

```
exec command: "cd ~/.openclaw/workspace && venv/bin/pip install python-pptx -q"
```

---

## 发送给用户（飞书）

生成完毕后，**只发 PPTX 文件**，不发预览图：

```python
# 以下用 exec 调用，替换变量后执行
import requests, json

APP_ID = "<从 SOUL.md/TOOLS.md 读取>"
APP_SECRET = "<从 SOUL.md/TOOLS.md 读取>"
OPEN_ID = "<用户 open_id>"

token = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
).json()["tenant_access_token"]
hdrs = {"Authorization": f"Bearer {token}"}

# 上传 PPTX
file_key = requests.post(
    "https://open.feishu.cn/open-apis/im/v1/files",
    headers=hdrs,
    files={"file": open("/tmp/sanwan_output.pptx", "rb")},
    data={"file_type": "stream", "file_name": "三万同款PPT.pptx"}
).json()["data"]["file_key"]

# 发送文件消息
requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={**hdrs, "Content-Type": "application/json"},
    json={
        "receive_id": OPEN_ID,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
)
```

---

## 注意事项

- `aspect_ratio` 必须传 `"16:9"`，否则输出为正方形
- 吉祥物每页必须出现，prompt_body 结尾单独用 `[MUST INCLUDE]` 强调位置和表情
- 白板边框描述用 `all four borders fully visible, zero background`，不用 `EXTREME CLOSE-UP`
- API Key 从 `~/.openclaw/openclaw.json` 的 `models.providers.deepv-easyclaw.apiKey` 读取
- 只发 PPTX 给用户，不发预览图片
