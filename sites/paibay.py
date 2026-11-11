# sites/paibay.py
from bs4 import BeautifulSoup

from models import BidItem, SiteUnreachable
from utils import (
    make_session, fetch, has_keyword, is_xinjiang, is_active,
    find_date_near_label,
)

SITE_NAME = "企优拍"

LIST_URL = "https://www.paibay.cn/index"


def scan() -> list[BidItem]:
    session = make_session()
    items: list[BidItem] = []

    try:
        resp = fetch(LIST_URL, session)
    except SiteUnreachable as e:
        raise SiteUnreachable(f"{SITE_NAME}: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select("a[href*='detail'], a[href*='auction'], a[href*='bid']"):
        title = a.get_text(strip=True)
        href = a.get("href", "")

        if not title or not has_keyword(title):
            continue
        if not is_xinjiang(title):
            continue

        if href.startswith("/"):
            detail_url = "https://www.paibay.cn" + href
        elif href.startswith("http"):
            detail_url = href
        else:
            detail_url = "https://www.paibay.cn/" + href

        try:
            detail_resp = fetch(detail_url, session)
            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

            start = find_date_near_label(detail_soup, "开始时间")
            end = find_date_near_label(detail_soup, "截止时间")

            if end and not is_active(start, end):
                continue

            items.append(BidItem(
                title=title, url=detail_url,
                start_time=start, end_time=end,
                site_name=SITE_NAME,
            ))
        except SiteUnreachable:
            continue

    return items