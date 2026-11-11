# main.py
import csv
import os
import traceback
from datetime import datetime

from config import OUTPUT_DIR
from models import BidItem, SiteUnreachable
from sites import ejy365_xinjiang

SITES = [
    ("e交易（新疆专区）", ejy365_xinjiang),
]


def generate_text(unique_items: list[BidItem], out_path: str) -> str:
    """生成纯文本报告，返回文本内容用于微信推送"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"📅 每日招标监控 ({now_str})")
    lines.append(f"🔥 今日符合条件：{len(unique_items)} 条\n")

    if not unique_items:
        lines.append("💤 今日暂无符合条件（新疆+废旧物资+进行中）的招标项目。")
    else:
        for idx, it in enumerate(unique_items, 1):
            # 格式化时间：如果时分是 00:00，就只显示日期
            if it.end_time:
                if it.end_time.hour == 0 and it.end_time.minute == 0:
                    end_str = it.end_time.strftime("%Y年%m月%d日")
                else:
                    end_str = it.end_time.strftime("%Y年%m月%d日 %H:%M")
            else:
                end_str = "未标明"

            # 用 Emoji 数字前缀
            emoji_num = f"{idx}️⃣" if idx <= 10 else f"[{idx}]"

            lines.append(f"{emoji_num} {it.title}")
            lines.append(f"🏢 来源：{it.site_name}")
            lines.append(f"⏰ 截止：{end_str}")
            lines.append(f"🔗 链接：{it.url}")
            lines.append("━━━━━━━━━━━━━━━")  # 分割线

    text_content = "\n".join(lines)

    # 保存到本地文件
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    print("\n" + "=" * 40)
    print("纯文本预览内容:")
    print("=" * 40)
    print(text_content)
    print("=" * 40)

    return text_content


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_items: list[BidItem] = []
    failures: list[tuple[str, str]] = []

    print("=" * 60)
    print("招标爬虫启动  |  目标：新疆 · 废旧/报废/闲置资产 · 进行中")
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

    # 输出 CSV (后台留档用)
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

    # 输出 TXT 并获取文本内容
    txt_path = os.path.join(OUTPUT_DIR, f"report_{ts}.txt")
    text_content = generate_text(unique, txt_path)

    # ====================================================
    # ===== 推送到微信 =====
    # ====================================================
    try:
        from push_wechat import send_to_wechat
        print("\n[调试] 正在发送微信推送...")

        # 调用推送函数，标题带上今日的数量
        title = f"新疆招标监控: 今日 {len(unique)} 条"
        send_to_wechat(title, text_content)
    except Exception as e:
        print(f"❌ 微信推送模块运行出错: {e}")
    # ====================================================

    # 汇总
    print(f"\n[完成] 共 {len(unique)} 条符合条件")
    print(f"CSV 文件已保存至: {csv_path}")
    print(f"TXT 文件已保存至: {txt_path}")

    if failures:
        print("\n无法正常访问 / 无法抓取的网站:")
        for name, reason in failures:
            print(f"  ✗ {name}")
            print(f"    原因: {reason}")
    print("=" * 60)


if __name__ == "__main__":
    main()