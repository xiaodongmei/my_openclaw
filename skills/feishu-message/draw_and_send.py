#!/usr/bin/env python3
"""
画图并自动发飞书 - 一体化脚本
用法：python3 draw_and_send.py "prompt描述" [ratio] [size]

ratio: auto | 1:1 | 16:9 | 9:16 （默认 auto）
size:  1k | 2k | 4k （默认 1k）

示例：
  python3 draw_and_send.py "一只可爱的橘猫"
  python3 draw_and_send.py "未来家庭机器人" auto 1k
  python3 draw_and_send.py "卖火柴的小女孩" 1:1 2k
"""

import sys
import os
import json
import subprocess

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
SEND_SCRIPT = os.path.join(SKILL_DIR, "send_image.py")
PYTHON = sys.executable


def generate_image(prompt: str, ratio: str, size: str) -> str:
    """调用 dvcode nanobanana 生成图片，返回图片 URL"""
    cmd_arg = f"/nanobanana {ratio} {size} {prompt}"
    print(f"[生成] 开始画图: {prompt} (ratio={ratio}, size={size})", flush=True)

    proc = subprocess.Popen(
        ["dvcode", "--output-format", "stream-json", "--yolo", cmd_arg],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    image_url = None
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            t = obj.get("type", "")
            if t == "nanobanana_submitted":
                est = obj.get("estimated_time_seconds", "?")
                print(f"[提交] 任务已提交，预计 {est} 秒完成", flush=True)
            elif t == "nanobanana_progress":
                pct = obj.get("progress_percent", 0)
                elapsed = obj.get("elapsed_seconds", 0)
                print(f"[进度] {pct}% ({elapsed}s)", flush=True)
            elif t == "nanobanana_completed":
                urls = obj.get("image_urls", [])
                if urls:
                    image_url = urls[0]
                print(f"[完成] 图片URL: {image_url}", flush=True)
        except json.JSONDecodeError:
            pass

    proc.wait()
    return image_url


def main():
    if len(sys.argv) < 2:
        print("用法: python3 draw_and_send.py \"prompt描述\" [ratio] [size]")
        sys.exit(1)

    prompt = sys.argv[1]
    ratio = sys.argv[2] if len(sys.argv) > 2 else "auto"
    size = sys.argv[3] if len(sys.argv) > 3 else "1k"

    image_url = generate_image(prompt, ratio, size)

    if not image_url:
        print("[错误] 未获取到图片URL，生成失败", flush=True)
        sys.exit(1)

    print("[发送] 正在发送到飞书...", flush=True)
    result = subprocess.run(
        [PYTHON, SEND_SCRIPT, image_url],
        capture_output=False
    )
    if result.returncode != 0:
        print("[错误] 发送失败", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
