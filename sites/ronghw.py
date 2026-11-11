# sites/ronghw.py
from bs4 import BeautifulSoup

from models import BidItem, SiteUnreachable
from utils import make_session, fetch, has_keyword, is_xinjiang

SITE_NAME = "中国融通电子商务平台"

LIST_URL = "https://www.ronghw.cn/dispose/package/list"


def scan() -> list[BidItem]:
    session = make_session()
    items: list[BidItem] = []

    try:
        resp = fetch(LIST_URL, session)
    except SiteUnreachable:
        raise SiteUnreachable(f"{SITE_NAME}: 无法访问")

    soup = BeautifulSoup(resp.text, "html.parser")

    # 融通列表页可能在 JS 中渲染，requests 拿不到时返回空
    for a in soup.select("a[href*='notice'], a[href*='package']"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or not has_keyword(title):
            continue
        if not is_xinjiang(title):
            continue

        if href.startswith("/"):
            detail_url = "https://www.ronghw.cn" + href
        elif href.startswith("http"):
            detail_url = href
        else:
            continue

        items.append(BidItem(
            title=title, url=detail_url,
            start_time=None, end_time=None,
            site_name=SITE_NAME,
        ))

    if not items and "ronghw" in resp.text.lower():
        # 页面有内容但匹配不到，可能是 JS 渲染
        pass

    return items