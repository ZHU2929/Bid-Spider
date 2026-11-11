# sites/ejy365_xinjiang.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

from models import BidItem, SiteUnreachable
from utils import has_keyword, parse_date, is_active

SITE_NAME = "e交易（新疆专区）"
TARGET_URL = "https://xjcqjy.ejy365.com/EJY/project?Headid=3&projectType=001001004&status=1"


def scan() -> list[BidItem]:
    items: list[BidItem] = []

    with sync_playwright() as p:
        # 【修改这里】改为 headless=True，彻底后台静默运行
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print("  [调试] 正在后台静默加载列表页...")
            page.goto(TARGET_URL, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_selector("#newHallList tr", timeout=15000)
            page.wait_for_timeout(3000)
        except Exception as e:
            browser.close()
            raise SiteUnreachable(f"{SITE_NAME}: 列表页加载失败 - {e}")

        list_html = page.content()
        browser.close()

    soup = BeautifulSoup(list_html, "html.parser")

    for row in soup.select("#newHallList tr"):
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        # 提取项目名称
        title = cells[1].get_text(strip=True)
        if not title or not has_keyword(title):
            continue

        # 提取核心的 infokey
        row_html = str(row)
        infokey_match = re.search(r"infokey=(ejy\d+)", row_html)
        if not infokey_match:
            continue
        infokey = infokey_match.group(1)

        # 提取截止时间
        end_text = cells[3].get_text(strip=True)
        end_time = parse_date(end_text)

        if end_time and not is_active(None, end_time):
            continue

        # 【直接拼装完美主站链接，不再进详情页请求】
        real_detail_url = f"https://www.ejy365.com/info/{infokey}"

        items.append(BidItem(
            title=title,
            url=real_detail_url,
            start_time=None,
            end_time=end_time,
            site_name=SITE_NAME,
        ))
        print(f"    ✔ 抓取到: {title[:30]}...")
        print(f"      URL: {real_detail_url}")

    return items