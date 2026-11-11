# sites/jd_auction.py
from models import BidItem, SiteUnreachable

SITE_NAME = "京东拍卖"


def scan() -> list[BidItem]:
    import requests
    from config import REQUEST_TIMEOUT, USER_AGENT

    try:
        r = requests.get(
            "https://auction.jd.com/",
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code in (403, 412):
            raise SiteUnreachable(f"{SITE_NAME}: 访问被拦截（HTTP {r.status_code}）")
        if "验证" in r.text[:500] or "安全" in r.text[:500]:
            raise SiteUnreachable(f"{SITE_NAME}: 返回验证页面，反爬拦截")
        if r.status_code >= 500:
            raise SiteUnreachable(f"{SITE_NAME}: HTTP {r.status_code}")
    except requests.RequestException as e:
        raise SiteUnreachable(f"{SITE_NAME}: {e}")

    raise SiteUnreachable(
        f"{SITE_NAME}: 可达但列表页需要浏览器渲染 + 风控 Cookie，纯 requests 无法稳定抓取"
    )