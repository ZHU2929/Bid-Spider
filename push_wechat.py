# push_wechat.py
import requests

# 把你的 PushPlus Token 填在这里
PUSHPLUS_TOKEN = "50e72c3ea04b496c900322b89e810230"


def send_to_wechat(title: str, markdown_content: str):
    url = "https://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": markdown_content,
        "template": "markdown"
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        result = resp.json()
        if result.get("code") == 200:
            print("✅ 微信推送成功！")
        else:
            print(f"❌ 微信推送失败: {result}")
    except Exception as e:
        print(f"❌ 推送异常: {e}")