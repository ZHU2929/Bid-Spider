# sites/sf_taobao.py
from models import BidItem, SiteUnreachable

SITE_NAME = "淘宝司法拍卖"


def scan() -> list[BidItem]:
    import requests
    from config import REQUEST_TIMEOUT, USER_AGENT

    try:
        r = requests.get(
            "https://sf.taobao.com/",
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code in (403, 412):
            raise SiteUnreachable(f"{SITE_NAME}: 访问被拦截（HTTP {r.status_code}）")
        if "登录" in r.text[:1000] and "滑块" in r.text[:1000]:
            raise SiteUnreachable(f"{SITE_NAME}: 需要登录 + 滑块验证，requests 无法通过")
    except requests.RequestException as e:
        raise SiteUnreachable(f"{SITE_NAME}: {e}")

    raise SiteUnreachable(
        f"{SITE_NAME}: 需要 Selenium/Playwright 手动登录过滑块，纯 requests 无法获取"
    )