"""Build one Pinterest RSS feed per board from pins.json.

Run from the repository root:  python3 scripts/build_feeds.py
Writes feeds/<board-slug>.xml. Pinterest checks each feed and turns
every new item into a pin on the board that feed is connected to.
"""
import json
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

SITE = "https://fridgepaper.co"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    with open(os.path.join(ROOT, "pins.json"), encoding="utf-8") as f:
        data = json.load(f)

    updated = datetime.strptime(data.get("updated", "2026-01-01"), "%Y-%m-%d")
    default_date = updated.replace(hour=12, tzinfo=timezone.utc)

    boards = {}
    for pin in data["pins"]:
        boards.setdefault(pin["board"], []).append(pin)

    out_dir = os.path.join(ROOT, "feeds")
    os.makedirs(out_dir, exist_ok=True)

    for board, pins in boards.items():
        name = slug(board)
        feed_url = f"{SITE}/feeds/{name}.xml"
        items = []
        for pin in pins:
            link = f"{SITE}/{pin['link'].lstrip('/')}"
            image = f"{SITE}/pins/{pin['image']}"
            img_path = os.path.join(ROOT, "pins", pin["image"])
            size = os.path.getsize(img_path)
            kind = "image/jpeg" if pin["image"].lower().endswith((".jpg", ".jpeg")) else "image/png"
            if pin.get("date"):
                when = datetime.strptime(pin["date"], "%Y-%m-%d").replace(hour=12, tzinfo=timezone.utc)
            else:
                when = default_date
            items.append(
                "    <item>\n"
                f"      <title>{escape(pin['title'])}</title>\n"
                f"      <link>{escape(link)}</link>\n"
                f"      <guid isPermaLink=\"false\">{escape(pin['image'])}</guid>\n"
                f"      <description>{escape(pin['description'])}</description>\n"
                f"      <pubDate>{format_datetime(when)}</pubDate>\n"
                f"      <enclosure url=\"{escape(image)}\" length=\"{size}\" type=\"{kind}\"/>\n"
                f"      <media:content url=\"{escape(image)}\" medium=\"image\" type=\"{kind}\"/>\n"
                "    </item>"
            )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" '
            'xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "  <channel>\n"
            f"    <title>FridgePaper: {escape(board)}</title>\n"
            f"    <link>{SITE}/</link>\n"
            f"    <atom:link href=\"{feed_url}\" rel=\"self\" type=\"application/rss+xml\"/>\n"
            f"    <description>Free printables from FridgePaper for the {escape(board)} board.</description>\n"
            "    <language>en-us</language>\n"
            f"    <lastBuildDate>{format_datetime(default_date)}</lastBuildDate>\n"
            + "\n".join(items)
            + "\n  </channel>\n</rss>\n"
        )
        with open(os.path.join(out_dir, f"{name}.xml"), "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"{feed_url}  ({len(pins)} pins)")


if __name__ == "__main__":
    main()
