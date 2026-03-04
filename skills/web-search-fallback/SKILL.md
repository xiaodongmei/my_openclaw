---
name: 网络搜索备选方案
description: 当 web_search 工具因缺少API Key无法使用时，通过 exec 工具调用 curl 进行网络搜索和网页抓取。当 web_search 返回 missing_brave_api_key 错误时使用此方案。
metadata: {"clawdbot":{"emoji":"globe"}}
---

# 网络搜索备选方案

当 web_search 工具返回 missing_brave_api_key 错误时，使用以下替代方案。

## 重要：优先使用此备选方案

如果 web_search 返回 API Key 缺失错误，不要告诉用户"无法搜索"，而是自动切换到以下方案。

## 方案1：通过 DuckDuckGo 搜索（无需 API Key）

  exec command: "curl -s 'https://html.duckduckgo.com/html/?q=查询关键词' -H 'User-Agent: Mozilla/5.0' | grep -oP '<a rel=.nofollow. class=.result__a. href=.\K[^"]+' | head -10"

或更简洁的方式：
  exec command: "curl -s 'https://lite.duckduckgo.com/lite/?q=关键词' -H 'User-Agent: Mozilla/5.0' | sed -n 's/.*<a[^>]*href="\([^"]*\)"[^>]*class="result-link"[^>]*//p' | head -10"

## 方案2：直接抓取网页内容

  exec command: "curl -sL 'https://目标网址' -H 'User-Agent: Mozilla/5.0' | head -200"

对于金价等实时数据：
  exec command: "curl -sL 'https://www.kitco.com/charts/livegold.html' -H 'User-Agent: Mozilla/5.0' | grep -i 'price\|gold\|USD' | head -20"

## 方案3：通过搜索引擎抓取

Google搜索（提取结果）：
  exec command: "curl -sL 'https://www.google.com/search?q=关键词&hl=zh-CN' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' | python3 -c 'import sys,re; html=sys.stdin.read(); [print(m) for m in re.findall(r"<h3[^>]*>(.*?)</h3>", html)[:10]]'"

## 方案4：API 数据源（金融数据）

金价实时数据：
  exec command: "curl -s 'https://api.exchangerate-api.com/v4/latest/XAU' 2>/dev/null || curl -s 'https://www.metals-api.com/api/latest?access_key=YOUR_KEY&base=XAU' 2>/dev/null"

## 注意

- 始终先尝试 web_search 工具
- 如果失败，自动切换到 exec + curl 方案
- 不要告诉用户"无法搜索"，要主动尝试备选方案
- curl 抓取时注意设置 User-Agent，避免被拦截
