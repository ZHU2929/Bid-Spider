# main.py
import csv
import os
import traceback
from datetime import datetime

from config import OUTPUT_DIR
from models import BidItem, SiteUnreachable
from sites import ejy365_xinjiang

# 只保留 e交易（新疆专区）
SITES = [
    ("e交易（新疆专区）", ejy365_xinjiang),
]


def generate_markdown(unique_items: list[BidItem], out_path: str):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"# 每日招标监控报告 ({now_str})")
    lines.append(f"\n**今日符合条件总数: {len(unique_items)} 条**\n")

    if not unique_items:
        lines.append("> 今日暂无符合条件（新疆+废旧物资+进行中）的招标项目。")
    else:
        for idx, it in enumerate(unique_items, 1):
            if it.end_time:
                if it.end_time.hour == 0 and it.end_time.minute == 0:
                    end_str = it.end_time.strftime("%Y年%m月%d日")
                else:
                    end_str = it.end_time.strftime("%Y年%m月%d日 %H:%M")
            else:
                end_str = "未标明"

            lines.append(f"### {idx}. {it.title}")
            lines.append(f"- **网站**: {it.site_name}")
            lines.append(f"- **截止时间**: {end_str}")
            lines.append(f"- **详情链接**: [点击查看详情页]({it.url})")
            lines.append("")

    md_content = "\n".join(lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + "=" * 40)
    print("Markdown 预览内容:")
    print("=" * 40)
    print(md_content)
    print("=" * 40)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_items: list[BidItem] = []
    failures: list[tuple[str, str]] = []

    print("=" * 60)
    print("招标爬虫启动  |  目标：新疆 · 废旧/报废/闲置资产 · 进行中")
    print("当前仅爬取：e交易（新疆专区）")
    print("=" * 60)

    for site_name, module in SITES:
        print(f"\n>>> {site_name}")
        try:
            items = module.scan()
            all_items.extend(items)
            print(f"    符合条件: {len(items)} 条")
        except SiteUnreachable as e:
            failures.append((site_name, str(e)))
            print(f"    ⚠ {e}")
        except Exception as e:
            failures.append((site_name, f"未预期异常: {e}"))
            traceback.print_exc()

    # 按 URL 去重
    seen = set()
    unique: list[BidItem] = []
    for it in all_items:
        if it.url not in seen:
            seen.add(it.url)
            unique.append(it)

    # 输出 CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"result_ejy365_{ts}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["标题", "详情页链接", "开始时间", "结束时间", "网站名"])
        for it in unique:
            writer.writerow([
                it.title, it.url,
                it.start_time.strftime("%Y-%m-%d %H:%M") if it.start_time else "",
                it.end_time.strftime("%Y-%m-%d %H:%M") if it.end_time else "",
                it.site_name,
            ])

    # 输出 Markdown
    md_path = os.path.join(OUTPUT_DIR, f"report_{ts}.md")
    generate_markdown(unique, md_path)

    # ====================================================
    # ===== 新增：推送到微信 =====
    # ====================================================
    try:
        from push_wechat import send_to_wechat
        print("\n[调试] 正在发送微信推送...")
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 调用推送函数，标题带上今日的数量
        title = f"新疆招标监控: 今日 {len(unique)} 条"
        send_to_wechat(title, md_content)
    except Exception as e:
        print(f"❌ 微信推送模块运行出错: {e}")
    # ====================================================

    # 汇总
    print(f"\n[完成] 共 {len(unique)} 条符合条件")
    print(f"CSV 文件已保存至: {csv_path}")
    print(f"Markdown 文件已保存至: {md_path}")

    if failures:
        print("\n无法正常访问 / 无法抓取的网站:")
        for name, reason in failures:
            print(f"  ✗ {name}")
            print(f"    原因: {reason}")
    else:
        print("\n所有网站均正常返回。")
    print("=" * 60)


if __name__ == "__main__":
    main()