# sites/caa123.py
import re
from bs4 import BeautifulSoup

from models import BidItem, SiteUnreachable
from utils import make_session, fetch, has_keyword, is_xinjiang, parse_date

SITE_NAME = "中拍平台"

# 中拍平台搜索接口（GET 方式，关键词拼接）
SEARCH_URL = "https://paimai.caa123.org.cn/pages/meeting/list.html?keyword={kw}"


def scan() -> list[BidItem]:
    session = make_session()
    items: list[BidItem] = []
    seen = set()

    # 用几个核心关键词分别搜
    search_keywords = ["新疆 废旧", "新疆 报废", "新疆 闲置"]

    for kw in search_keywords:
        url = SEARCH_URL.format(kw=kw.replace(" ", "%20"))
        try:
            resp = fetch(url, session)
        except SiteUnreachable:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a[href*='conference.html'], a[href*='meeting']"):
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or not has_keyword(title):
                continue
            if not is_xinjiang(title):
                continue

            if href.startswith("/"):
                detail_url = "https://paimai.caa123.org.cn" + href
            elif href.startswith("http"):
                detail_url = href
            else:
                continue

            if detail_url in seen:
                continue
            seen.add(detail_url)

            try:
                detail_resp = fetch(detail_url, session)
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                text = detail_soup.get_text(" ", strip=True)

                # 中拍详情页有“拍卖时间”或“网络在线竞价时间”
                start = None
                end = None
                m = re.search(
                    r"(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})[时:：](\d{1,2})?",
                    text,
                )
                if m:
                    start = parse_date(m.group(0))

                # 如果有“至”后面的时间作为结束
                m2 = re.search(
                    r"至\s*(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})[时:：]",
                    text,
                )
                if m2:
                    end = parse_date(m2.group(1) + "年" + m2.group(2) + "月"
                                     + m2.group(3) + "日" + m2.group(4) + "时")

                if end and end < __import__("datetime").datetime.now():
                    continue

                items.append(BidItem(
                    title=title, url=detail_url,
                    start_time=start, end_time=end,
                    site_name=SITE_NAME,
                ))
            except SiteUnreachable:
                continue

    return items