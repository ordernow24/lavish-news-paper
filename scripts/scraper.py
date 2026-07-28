"""
LAVISH NEWS PAPER — News Scraper
Har 4 ghante me chalta hai. RSS feeds se news uthata hai,
duplicate check karta hai, aur data/pending/ me category-wise save karta hai.
"""

import feedparser
import json
import os
import hashlib
import logging
from datetime import datetime
import config

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [SCRAPER] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def make_id(title, link):
    """Unique hash so we never store the same news twice."""
    raw = (title.strip().lower() + link.strip().lower()).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def load_existing_ids(category):
    """Load IDs already collected today so duplicates are skipped."""
    path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
    if not os.path.exists(path):
        return [], []
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return items, [i["id"] for i in items]


def save_items(category, items):
    os.makedirs(config.DATA_PENDING_DIR, exist_ok=True)
    path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def scrape_category(category, sources):
    existing_items, existing_ids = load_existing_ids(category)
    new_count = 0
    error_count = 0

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])

            if feed.bozo and not feed.entries:
                logger.warning(f"Feed broken/unreachable: {source['name']} ({source['url']})")
                error_count += 1
                continue

            for entry in feed.entries[:15]:  # cap per source per run to control load
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "")

                if not title or not link:
                    continue  # detector: skip broken/empty entries

                if len(title) < 8:
                    continue  # detector: too short to be a real headline

                item_id = make_id(title, link)
                if item_id in existing_ids:
                    continue  # detector: duplicate skip

                published = getattr(entry, "published", datetime.utcnow().isoformat())

                existing_items.append({
                    "id": item_id,
                    "title": title,
                    "raw_summary": summary,
                    "link": link,
                    "source": source["name"],
                    "weight": source["weight"],
                    "published": published,
                    "collected_at": datetime.utcnow().isoformat(),
                    "summarized": False,
                    "summary_en": "",
                    "summary_hi": "",
                })
                existing_ids.append(item_id)
                new_count += 1

        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
            error_count += 1

    save_items(category, existing_items)
    logger.info(f"[{category}] +{new_count} new items, {error_count} source errors, total={len(existing_items)}")
    return new_count, error_count


def run():
    logger.info("===== Scrape run started =====")
    total_new, total_errors = 0, 0
    for category, sources in config.RSS_SOURCES.items():
        n, e = scrape_category(category, sources)
        total_new += n
        total_errors += e
    logger.info(f"===== Scrape run finished: {total_new} new items, {total_errors} errors =====")
    print(f"Scrape complete: {total_new} new items collected, {total_errors} source errors logged.")


if __name__ == "__main__":
    run()
