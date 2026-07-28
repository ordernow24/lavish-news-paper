"""
LAVISH NEWS PAPER — Detector / Recheck Module
Har 4-ghante ke run ke baad aur final publish se pehle chalta hai.
Quality checks: duplicates, broken links, empty/short content,
weird characters, oversized text. Bad items ko "flagged" me daal deta hai
taaki wo PDF me na jayein, lekin pipeline kabhi crash na ho.
"""

import json
import os
import re
import logging
import config

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [DETECTOR] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def is_valid_url(url):
    return bool(re.match(r"^https?://[^\s]+\.[^\s]{2,}", url or ""))


def has_suspicious_content(text):
    """Flag near-empty, placeholder, or garbled text."""
    if not text or len(text.strip()) < 15:
        return True
    if text.strip().lower() in ("none", "n/a", "null", "..."):
        return True
    # too many repeated characters = likely garbled scrape
    if re.search(r"(.)\1{6,}", text):
        return True
    return False


def check_item(item):
    """Returns (is_ok: bool, reasons: list[str])"""
    reasons = []

    if not item.get("title") or len(item["title"].strip()) < 8:
        reasons.append("title_too_short")

    if not is_valid_url(item.get("link", "")):
        reasons.append("broken_link")

    if not item.get("summarized"):
        reasons.append("not_summarized")

    summary_en = item.get("summary_en", "")
    if has_suspicious_content(summary_en):
        reasons.append("empty_or_bad_english_summary")

    if len(summary_en.split()) > 200:
        reasons.append("summary_too_long")

    return (len(reasons) == 0), reasons


def dedupe_across_categories(all_items_by_cat):
    """Same story sometimes appears via 2 different feeds — dedupe by title similarity."""
    seen_titles = set()
    for category, items in all_items_by_cat.items():
        unique = []
        for item in items:
            key = re.sub(r"[^a-z0-9]", "", item["title"].lower())[:60]
            if key in seen_titles:
                continue
            seen_titles.add(key)
            unique.append(item)
        all_items_by_cat[category] = unique
    return all_items_by_cat


def run_recheck():
    logger.info("===== Detector recheck started =====")
    all_items = {}
    report = {"ok": 0, "flagged": 0, "details": []}

    for category in config.RSS_SOURCES.keys():
        path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
        if not os.path.exists(path):
            all_items[category] = []
            continue
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        all_items[category] = items

    all_items = dedupe_across_categories(all_items)

    for category, items in all_items.items():
        clean_items = []
        for item in items:
            ok, reasons = check_item(item)
            if ok:
                clean_items.append(item)
                report["ok"] += 1
            else:
                report["flagged"] += 1
                report["details"].append({"title": item.get("title", "?")[:60], "category": category, "reasons": reasons})
                logger.warning(f"Flagged [{category}] '{item.get('title','?')[:50]}' -> {reasons}")

        path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_items, f, ensure_ascii=False, indent=2)

    logger.info(f"===== Detector finished: {report['ok']} OK, {report['flagged']} flagged/removed =====")
    print(f"Recheck complete: {report['ok']} items OK, {report['flagged']} flagged and removed.")
    return report


if __name__ == "__main__":
    run_recheck()
