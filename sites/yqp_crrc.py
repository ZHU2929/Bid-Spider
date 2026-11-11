# sites/yqp_crrc.py
from models import BidItem, SiteUnreachable

SITE_NAME = "央企拍（yqp-crrc）"


def scan() -> list[BidItem]:
    # 该站点为 SPA（#/home 路由），列表数据由前端 XHR 加载。
    # 纯 requests 无法获取列表。此处探测可达性后提示。
    import requests
    from config import REQUEST_TIMEOUT, USER_AGENT

    try:
        r = requests.get(
            "https://www.yqp-crrc.com/",
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code >= 500:
            raise SiteUnreachable(f"{SITE_NAME}: HTTP {r.status_code}")
    except requests.RequestException as e:
        raise SiteUnreachable(f"{SITE_NAME}: {e}")

    raise SiteUnreachable(
        f"{SITE_NAME}: 页面为 SPA，requests 无法获取列表数据，需启用 Playwright 渲染"
    )