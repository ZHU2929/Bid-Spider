# sites/hepaiwang.py
from bs4 import BeautifulSoup

from models import BidItem, SiteUnreachable
from utils import make_session, fetch, has_keyword, is_xinjiang, parse_date

SITE_NAME = "和拍网"

LIST_URL = "https://www.hepaiwang.cn/myBuy/bidList"


def scan() -> list[BidItem]:
    session = make_session()
    items: list[BidItem] = []

    try:
        resp = fetch(LIST_URL, session)
    except SiteUnreachable:
        raise SiteUnreachable(f"{SITE_NAME}: 列表页不可达")

    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select("a[href*='bidDetail']"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or not has_keyword(title):
            continue
        if not is_xinjiang(title):
            continue

        if href.startswith("/"):
            detail_url = "https://www.hepaiwang.cn" + href
        elif href.startswith("http"):
            detail_url = href
        else:
            continue

        items.append(BidItem(
            title=title, url=detail_url,
            start_time=None, end_time=None,
            site_name=SITE_NAME,
        ))

    return items