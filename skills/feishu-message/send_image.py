#!/usr/bin/env python3
"""
发送图片/文件到飞书用户
用法：
  python3 send_image.py /path/to/image.png         # 发本地图片
  python3 send_image.py https://example.com/a.jpg  # 发网络图片（先下载）
  python3 send_image.py /path/to/file.pptx         # 发任意文件
"""

import sys
import os
import json
import uuid
import urllib.request
import tempfile

# ── 飞书配置（从 openclaw.json 或硬编码） ──────────────────────
FEISHU_APP_ID = "cli_a92abc6e2e395cc6"
FEISHU_APP_SECRET = "y2JmtAkrcsCVHn1wRKaWfbQ8vCeo0WJX"
FEISHU_USER_OPEN_ID = "ou_2a8de8097294e557f1d8ca5d08e91c63"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


def get_token():
    data = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    token = result.get("tenant_access_token", "")
    if not token:
        raise RuntimeError(f"获取 token 失败: {result}")
    return token


def download_url(url: str) -> str:
    """下载网络图片到临时文件，返回本地路径"""
    suffix = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        tmp.write(resp.read())
    tmp.close()
    print(f"[下载] {url} -> {tmp.name}", flush=True)
    return tmp.name


def send_image(token: str, filepath: str):
    """上传图片并发送图片消息"""
    boundary = uuid.uuid4().hex
    with open(filepath, "rb") as f:
        file_data = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image_type"\r\n\r\nmessage\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="image.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    upload_req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/images",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )
    with urllib.request.urlopen(upload_req, timeout=30) as resp:
        upload_result = json.loads(resp.read())

    if upload_result.get("code") != 0:
        raise RuntimeError(f"图片上传失败: {upload_result}")
    image_key = upload_result["data"]["image_key"]
    print(f"[上传] image_key={image_key}", flush=True)

    send_data = json.dumps({
        "receive_id": FEISHU_USER_OPEN_ID,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }).encode()
    send_req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        data=send_data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(send_req, timeout=10) as resp:
        send_result = json.loads(resp.read())

    if send_result.get("code") != 0:
        raise RuntimeError(f"图片发送失败: {send_result}")
    print(f"[OK] 图片已发送给用户", flush=True)


def send_file(token: str, filepath: str, filename: str = None):
    """上传文件并发送文件消息"""
    fname = filename or os.path.basename(filepath)
    boundary = uuid.uuid4().hex
    with open(filepath, "rb") as f:
        file_data = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file_type"\r\n\r\nstream\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file_name"\r\n\r\n{fname}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    upload_req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/files",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )
    with urllib.request.urlopen(upload_req, timeout=60) as resp:
        upload_result = json.loads(resp.read())

    if upload_result.get("code") != 0:
        raise RuntimeError(f"文件上传失败: {upload_result}")
    file_key = upload_result["data"]["file_key"]
    print(f"[上传] file_key={file_key}", flush=True)

    send_data = json.dumps({
        "receive_id": FEISHU_USER_OPEN_ID,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }).encode()
    send_req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        data=send_data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(send_req, timeout=10) as resp:
        send_result = json.loads(resp.read())

    if send_result.get("code") != 0:
        raise RuntimeError(f"文件发送失败: {send_result}")
    print(f"[OK] 文件 {fname} 已发送给用户", flush=True)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 send_image.py <文件路径或图片URL>")
        sys.exit(1)

    target = sys.argv[1]
    token = get_token()

    # 网络 URL → 先下载
    if target.startswith("http://") or target.startswith("https://"):
        local_path = download_url(target)
        ext = os.path.splitext(local_path)[1].lower()
        if ext in IMAGE_EXTS:
            send_image(token, local_path)
        else:
            send_file(token, local_path)
        os.unlink(local_path)
        return

    # 本地文件
    if not os.path.exists(target):
        print(f"[错误] 文件不存在: {target}", flush=True)
        sys.exit(1)

    ext = os.path.splitext(target)[1].lower()
    if ext in IMAGE_EXTS:
        send_image(token, target)
    else:
        send_file(token, target)


if __name__ == "__main__":
    main()
