# push_wechat.py
import os
import requests

# 去 https://www.pushplus.plus/ 微信扫码登录，复制你的 Token 填在这里
# 如果是在 GitHub 上跑，代码会自动读取你配置的 Secrets
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "50e72c3ea04b496c900322b89e810230")


def send_to_wechat(title: str, text_content: str):
    url = "https://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": text_content,
        "template": "txt"  # 【修改这里】改用纯文本模式，微信阅读体验最好
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