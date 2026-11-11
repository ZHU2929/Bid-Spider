# sites/ggzy_gov.py
from models import BidItem, SiteUnreachable

SITE_NAME = "全国公共资源交易平台"


def scan() -> list[BidItem]:
    import requests
    from config import REQUEST_TIMEOUT, USER_AGENT

    try:
        r = requests.get(
            "https://www.ggzy.gov.cn/",
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code >= 500:
            raise SiteUnreachable(f"{SITE_NAME}: HTTP {r.status_code}")
    except requests.Timeout:
        raise SiteUnreachable(f"{SITE_NAME}: 连接超时（该平台历史上有不可达记录）")
    except requests.RequestException as e:
        raise SiteUnreachable(f"{SITE_NAME}: {e}")

    raise SiteUnreachable(
        f"{SITE_NAME}: 可达但需要 Playwright 绕过 WAF，且新疆筛选需结合地方站点"
    )