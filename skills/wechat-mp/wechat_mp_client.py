#!/usr/bin/env python3
"""
微信公众号操作客户端 v2
通过 agent-browser + 微信后台API 实现稳定操作：
- 登录（扫码）
- 查看文章列表和数据
- 创建草稿
- 发布文章
- 获取账号信息

使用方法:
  python3 wechat_mp_client.py login          # 登录（获取二维码）
  python3 wechat_mp_client.py login_confirm  # 确认扫码
  python3 wechat_mp_client.py status         # 检查登录状态
  python3 wechat_mp_client.py articles       # 获取已发布文章列表
  python3 wechat_mp_client.py drafts         # 获取草稿箱列表
  python3 wechat_mp_client.py article_stats  # 获取最新文章数据
  python3 wechat_mp_client.py publish '{"title":"标题","content":"内容","author":"作者"}'
  python3 wechat_mp_client.py account_info   # 获取账号信息
"""

import subprocess
import json
import sys
import os
import time
import urllib.request
import urllib.parse

# 配置
MP_URL = "https://mp.weixin.qq.com"
SESSION_NAME = "wechat-mp"
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/data/wechat-mp-state.json")
QR_SCREENSHOT = os.path.expanduser("~/.openclaw/workspace/data/wechat-mp-qr.png")

# 飞书配置
FEISHU_APP_ID = "cli_a92abc6e2e395cc6"
FEISHU_APP_SECRET = "y2JmtAkrcsCVHn1wRKaWfbQ8vCeo0WJX"
FEISHU_USER_OPEN_ID = "ou_2a8de8097294e557f1d8ca5d08e91c63"

os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)


# ============ 工具函数 ============

def run_ab(cmd_args, timeout=30):
    """执行 agent-browser 命令"""
    full_cmd = f"agent-browser --session {SESSION_NAME} {cmd_args}"
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr.strip():
            return {"success": False, "error": result.stderr.strip()}
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"success": True, "data": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "命令超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_ab_eval(js_code, timeout=30):
    """在浏览器中执行JS代码并返回结果"""
    # 转义引号
    escaped = js_code.replace("'", "'\\''")
    result = run_ab(f"eval '{escaped}'", timeout=timeout)
    if isinstance(result, dict) and result.get("success") is False:
        return result
    # agent-browser eval 返回的是字符串形式的结果
    data = result.get("data", result) if isinstance(result, dict) else result
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            # 可能是双重JSON编码
            try:
                return json.loads(json.loads(data))
            except Exception:
                return {"data": data}
    return data


TOKEN_FILE = os.path.expanduser("~/.openclaw/workspace/data/wechat-mp-token.txt")


def _get_url():
    """获取当前浏览器URL"""
    url_result = run_ab("get url --json")
    if isinstance(url_result, dict):
        d = url_result.get("data", {})
        if isinstance(d, dict):
            return d.get("url", "")
        return str(d)
    return str(url_result)


def get_token():
    """获取微信后台token，多种方式尝试"""
    import re

    # 1. 从URL提取
    url = _get_url()
    match = re.search(r'token=(\d+)', url)
    if match:
        token = match.group(1)
        # 缓存到文件
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        return token

    # 2. 从页面内的链接/脚本中提取
    result = run_ab_eval("""
    var html = document.documentElement.innerHTML;
    var m = html.match(/token[=:]\\s*['\"]?(\\d{6,})/);
    if (m) m[1]; else {
        var links = document.querySelectorAll('a[href*=\"token=\"]');
        var found = null;
        for (var i = 0; i < links.length; i++) {
            var hm = links[i].href.match(/token=(\\d{6,})/);
            if (hm) { found = hm[1]; break; }
        }
        found || '';
    }
    """)
    if isinstance(result, dict):
        val = result.get("data", "")
    else:
        val = str(result) if result else ""
    if val and val.isdigit() and len(val) >= 6:
        with open(TOKEN_FILE, "w") as f:
            f.write(val)
        return val

    # 3. 从缓存文件读取
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            cached = f.read().strip()
        if cached:
            return cached

    return None


def mp_api(endpoint, params=None, post_data=None, timeout=20):
    """通过浏览器fetch调用微信后台API"""
    token = get_token()
    if not token:
        return {"error": "无法获取token，请重新登录"}

    base_params = f"token={token}&lang=zh_CN&f=json&ajax=1"
    if params:
        base_params += "&" + params

    url = f"/cgi-bin/{endpoint}?{base_params}"

    if post_data:
        js = f"""
        var formData = new URLSearchParams();
        var postObj = {json.dumps(post_data)};
        for (var k in postObj) {{ formData.append(k, postObj[k]); }}
        fetch('{url}', {{
          method: 'POST',
          credentials: 'include',
          headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
          body: formData.toString()
        }}).then(r => r.json()).then(d => JSON.stringify(d))
        """
    else:
        js = f"""
        fetch('{url}', {{credentials: 'include'}})
        .then(r => r.json())
        .then(d => JSON.stringify(d))
        """

    return run_ab_eval(js, timeout=timeout)


def send_feishu_image(filepath):
    """通过飞书API直接发送图片给用户"""
    try:
        import uuid
        token_data = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
        token_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            data=token_data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            token_resp = json.loads(resp.read())
        token = token_resp.get("tenant_access_token", "")
        if not token:
            return False

        boundary = uuid.uuid4().hex
        with open(filepath, "rb") as f:
            file_data = f.read()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image_type"\r\n\r\nmessage\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="qr.png"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
        upload_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/im/v1/images",
            data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        with urllib.request.urlopen(upload_req, timeout=15) as resp:
            upload_data = json.loads(resp.read())
        if upload_data.get("code") != 0:
            return False
        image_key = upload_data["data"]["image_key"]

        send_data = json.dumps({
            "receive_id": FEISHU_USER_OPEN_ID, "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }).encode()
        send_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            data=send_data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(send_req, timeout=10) as resp:
            send_resp = json.loads(resp.read())
        if send_resp.get("code") != 0:
            return False

        # 发送文字提示
        text_data = json.dumps({
            "receive_id": FEISHU_USER_OPEN_ID, "msg_type": "text",
            "content": json.dumps({"text": "请用微信扫描上方二维码登录公众号。扫码完成后回复我【已扫码】即可。"})
        }).encode()
        text_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            data=text_data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(text_req, timeout=10) as resp:
                pass
        except Exception:
            pass
        return True
    except Exception:
        return False


def upload_to_imghost(filepath):
    """上传到图床获取URL"""
    try:
        import uuid
        boundary = uuid.uuid4().hex
        with open(filepath, "rb") as f:
            file_data = f.read()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="reqtype"\r\n\r\nfileupload\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="fileToUpload"; filename="qr.png"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            "https://catbox.moe/user/api.php", data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode().strip()
            if result.startswith("http"):
                return result
    except Exception:
        pass
    return None


def ensure_logged_in():
    """确保已登录，返回是否成功。
    策略（不做page navigation，直接用fetch验证）：
    1. 从缓存读取token
    2. 在当前浏览器session中用fetch API验证token是否有效
    3. 如果有效直接返回True
    4. 如果无效清除缓存返回False
    注意：不做任何页面导航，避免丢失session。
    """
    token = get_token()
    if not token:
        return False

    # 用fetch验证token是否有效（不导航页面）
    test_js = f"""
    fetch('/cgi-bin/appmsg?action=list_ex&begin=0&count=1&type=9&token={token}&lang=zh_CN&f=json&ajax=1', {{
        credentials: 'include'
    }}).then(r => r.json()).then(d => JSON.stringify({{
        ok: (d.base_resp && d.base_resp.ret === 0) || !!d.app_msg_list,
        ret: d.base_resp ? d.base_resp.ret : -1
    }}))
    """
    test_result = run_ab_eval(test_js, timeout=15)

    if isinstance(test_result, dict) and test_result.get("ok"):
        return True

    # token无效，清除缓存
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    return False


# ============ 命令处理 ============

def cmd_login():
    """登录微信公众号"""
    print(json.dumps({"step": "opening", "message": "正在打开微信公众号登录页..."}, ensure_ascii=False), flush=True)

    run_ab(f"open {MP_URL}", timeout=20)
    time.sleep(4)
    run_ab("wait --load networkidle", timeout=15)

    # 检查是否已登录
    url_result = run_ab("get url --json")
    url = ""
    if isinstance(url_result, dict):
        d = url_result.get("data", {})
        url = d.get("url", str(d)) if isinstance(d, dict) else str(d)

    if "token=" in url and "home" in url:
        import re
        match = re.search(r'token=(\d+)', url)
        if match:
            with open(TOKEN_FILE, "w") as f:
                f.write(match.group(1))
        run_ab(f"state save {STATE_FILE}")
        print(json.dumps({"status": "already_logged_in", "message": "已经处于登录状态！"}, ensure_ascii=False))
        return

    # 截取二维码
    run_ab(f"screenshot {QR_SCREENSHOT}", timeout=10)

    # 尝试飞书直发
    if send_feishu_image(QR_SCREENSHOT):
        print(json.dumps({
            "status": "waiting_scan",
            "message": "二维码已通过飞书发送！请用微信扫码登录。扫码完成后告诉我。",
            "feishu_image_sent": True
        }, ensure_ascii=False))
        return

    # 降级：图床
    qr_url = upload_to_imghost(QR_SCREENSHOT)
    if qr_url:
        print(json.dumps({
            "status": "waiting_scan", "message": "请使用微信扫描二维码登录公众号",
            "qr_url": qr_url, "instruction": "请打开链接查看二维码并用微信扫码。"
        }, ensure_ascii=False))
    else:
        print(json.dumps({
            "status": "waiting_scan", "message": "请使用微信扫描二维码登录",
            "qr_screenshot": QR_SCREENSHOT
        }, ensure_ascii=False))


def cmd_login_confirm():
    """确认登录。扫码后立刻提取token并保存。"""
    import re
    print(json.dumps({"step": "confirming", "message": "正在确认登录状态..."}, ensure_ascii=False), flush=True)

    for waited in range(0, 60, 5):
        run_ab("wait --load networkidle", timeout=10)
        url = _get_url()

        # 方式1: URL中直接有token
        match = re.search(r'token=(\d+)', url)
        if match:
            with open(TOKEN_FILE, "w") as f:
                f.write(match.group(1))
            print(json.dumps({"status": "logged_in", "message": "登录成功！"}, ensure_ascii=False))
            return

        # 方式2: URL变了（跳转到了后台某个页面），从页面HTML提取token
        if "mp.weixin.qq.com/cgi-bin/" in url and "loginpage" not in url:
            result = run_ab_eval("""
            var html = document.documentElement.innerHTML;
            var m = html.match(/token[=:]\\s*['\"]?(\\d{6,})/);
            m ? m[1] : ''
            """)
            val = ""
            if isinstance(result, dict):
                val = result.get("data", "")
            else:
                val = str(result) if result else ""
            if val and val.isdigit() and len(val) >= 6:
                with open(TOKEN_FILE, "w") as f:
                    f.write(val)
                print(json.dumps({"status": "logged_in", "message": "登录成功！"}, ensure_ascii=False))
                return

        time.sleep(5)
        print(json.dumps({"step": "waiting", "message": f"等待扫码...({waited+5}/60秒)"}, ensure_ascii=False), flush=True)

    print(json.dumps({"status": "timeout", "message": "等待超时，请重新登录"}, ensure_ascii=False))


def cmd_status():
    """检查登录状态"""
    if ensure_logged_in():
        print(json.dumps({"status": "logged_in", "message": "已登录微信公众号后台"}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "not_logged_in", "message": "未登录，请使用 login 命令"}, ensure_ascii=False))


def cmd_articles():
    """获取已发布文章列表"""
    if not ensure_logged_in():
        print(json.dumps({"status": "error", "message": "未登录"}, ensure_ascii=False))
        return

    result = mp_api("appmsg", "action=list_ex&begin=0&count=10&type=9")

    if isinstance(result, dict) and "app_msg_list" in result:
        articles = []
        for a in result["app_msg_list"]:
            articles.append({
                "title": a.get("title", ""),
                "link": a.get("link", ""),
                "update_time": a.get("update_time", 0),
                "aid": a.get("aid", "")
            })
        print(json.dumps({
            "status": "success",
            "total": result.get("app_msg_cnt", 0),
            "articles": articles
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "获取失败", "detail": str(result)[:500]}, ensure_ascii=False))


def cmd_drafts():
    """获取草稿箱列表"""
    if not ensure_logged_in():
        print(json.dumps({"status": "error", "message": "未登录"}, ensure_ascii=False))
        return

    result = mp_api("appmsg", "action=list_ex&begin=0&count=10&type=10")

    if isinstance(result, dict) and "app_msg_list" in result:
        drafts = []
        for a in result["app_msg_list"]:
            drafts.append({
                "title": a.get("title", ""),
                "update_time": a.get("update_time", 0),
                "aid": a.get("aid", "")
            })
        print(json.dumps({
            "status": "success",
            "total": result.get("app_msg_cnt", 0),
            "drafts": drafts
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "获取失败", "detail": str(result)[:500]}, ensure_ascii=False))


def cmd_article_stats():
    """获取最新文章数据统计"""
    if not ensure_logged_in():
        print(json.dumps({"status": "error", "message": "未登录"}, ensure_ascii=False))
        return

    # 获取最新的已发布文章列表（type=9）
    result = mp_api("appmsg", "action=list_ex&begin=0&count=5&type=9")

    if isinstance(result, dict) and "app_msg_list" in result:
        articles = []
        for a in result["app_msg_list"]:
            articles.append({
                "title": a.get("title", ""),
                "read_num": a.get("read_num", "N/A"),
                "like_num": a.get("like_num", "N/A"),
                "update_time": a.get("update_time", 0),
                "link": a.get("link", "")
            })
        print(json.dumps({
            "status": "success",
            "message": "最新文章数据统计",
            "articles": articles
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "获取失败"}, ensure_ascii=False))


def cmd_publish(params_json):
    """创建草稿并可选发布"""
    if not ensure_logged_in():
        print(json.dumps({"status": "error", "message": "未登录"}, ensure_ascii=False))
        return

    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "参数格式错误，需要JSON"}, ensure_ascii=False))
        return

    title = params.get("title", "")
    content = params.get("content", "")
    author = params.get("author", "")
    digest = params.get("digest", "")

    if not title or not content:
        print(json.dumps({"status": "error", "message": "标题和内容不能为空"}, ensure_ascii=False))
        return

    # 将纯文本内容转换为HTML
    if not content.strip().startswith("<"):
        paragraphs = content.split("\n")
        content_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
    else:
        content_html = content

    print(json.dumps({"step": 1, "message": f"正在创建草稿: {title}"}, ensure_ascii=False), flush=True)

    token = get_token()
    if not token:
        print(json.dumps({"status": "error", "message": "无法获取token"}, ensure_ascii=False))
        return

    # 通过浏览器fetch创建草稿
    # 需要转义content_html中的特殊字符
    content_escaped = content_html.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
    title_escaped = title.replace("\\", "\\\\").replace("'", "\\'")
    author_escaped = author.replace("\\", "\\\\").replace("'", "\\'")
    digest_escaped = digest.replace("\\", "\\\\").replace("'", "\\'")

    js_code = f"""
    var formData = new URLSearchParams();
    formData.append('token', '{token}');
    formData.append('lang', 'zh_CN');
    formData.append('f', 'json');
    formData.append('ajax', '1');
    formData.append('AppMsgId', '');
    formData.append('count', '1');
    formData.append('data_seq', '0');
    formData.append('operate_from', 'Chrome');
    formData.append('isnew', '1');
    formData.append('title0', '{title_escaped}');
    formData.append('author0', '{author_escaped}');
    formData.append('writerid0', '');
    formData.append('fileid0', '');
    formData.append('digest0', '{digest_escaped}');
    formData.append('content0', '{content_escaped}');
    formData.append('sourceurl0', '');
    formData.append('need_open_comment0', '0');
    formData.append('only_fans_can_comment0', '0');
    formData.append('cdn_url0', '');
    formData.append('cdn_235_1_url0', '');
    formData.append('cdn_1_1_url0', '');
    formData.append('can_reward0', '0');
    formData.append('reward_wording0', '');
    formData.append('free_content0', '');
    formData.append('fee0', '0');
    formData.append('show_cover_pic0', '0');
    formData.append('shortvideofileid0', '');
    formData.append('copyright_type0', '0');

    fetch('/cgi-bin/operate_appmsg?t=ajax-response&sub=create&type=77&token={token}&lang=zh_CN', {{
      method: 'POST',
      credentials: 'include',
      headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
      body: formData.toString()
    }}).then(r => r.json()).then(d => JSON.stringify(d))
    """

    result = run_ab_eval(js_code, timeout=30)

    if isinstance(result, dict) and result.get("base_resp", {}).get("ret") == 0:
        app_msg_id = result.get("appMsgId", "")
        print(json.dumps({
            "status": "draft_created",
            "message": f"草稿创建成功！标题: {title}",
            "appMsgId": app_msg_id,
            "next_steps": "草稿已保存到公众号后台草稿箱。如需群发发布，请在公众号后台手动操作或告诉我发布。"
        }, ensure_ascii=False))
    else:
        err_msg = ""
        if isinstance(result, dict):
            err_msg = result.get("base_resp", {}).get("err_msg", str(result)[:300])
        print(json.dumps({
            "status": "error",
            "message": f"草稿创建失败: {err_msg}",
            "detail": str(result)[:500]
        }, ensure_ascii=False))


def cmd_account_info():
    """获取账号信息"""
    if not ensure_logged_in():
        print(json.dumps({"status": "error", "message": "未登录"}, ensure_ascii=False))
        return

    result = mp_api("settingpage", "action=index&t=setting/index")

    if isinstance(result, dict) and "setting_info" in result:
        info = result["setting_info"]
        print(json.dumps({
            "status": "success",
            "account_info": {
                "nickname": info.get("nickname", ""),
                "signature": info.get("signature", ""),
                "head_img": info.get("head_img_url", ""),
                "service_type": info.get("service_type_info", ""),
                "verify_type": info.get("verify_type_info", "")
            }
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "获取失败"}, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": {
                "login": "登录微信公众号（获取二维码截图）",
                "login_confirm": "确认扫码登录",
                "status": "检查登录状态",
                "articles": "获取已发布文章列表",
                "drafts": "获取草稿箱列表",
                "article_stats": "获取最新文章数据统计（阅读量、点赞数）",
                "publish": '创建并发布文章 (JSON参数: {"title":"标题","content":"内容","author":"作者"})',
                "account_info": "获取账号信息"
            }
        }, ensure_ascii=False, indent=2))
        return

    command = sys.argv[1]

    commands = {
        "login": cmd_login,
        "login_confirm": cmd_login_confirm,
        "status": cmd_status,
        "articles": cmd_articles,
        "drafts": cmd_drafts,
        "article_stats": cmd_article_stats,
        "account_info": cmd_account_info,
    }

    if command in commands:
        commands[command]()
    elif command == "publish":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "需要JSON参数"}, ensure_ascii=False))
            return
        cmd_publish(sys.argv[2])
    else:
        print(json.dumps({"error": f"未知命令: {command}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
