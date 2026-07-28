"""
LAVISH NEWS PAPER — Summarizer
Har 4-ghante ke run me chalta hai. Un items ko process karta hai
jo abhi tak summarize nahi hue (summarized: false).
Hugging Face free Inference API use karta hai — English + Hindi dono.
"""

import json
import os
import re
import time
import logging
import requests
import config

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [SUMMARIZER] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

HEADERS = {"Authorization": f"Bearer {config.HF_API_TOKEN}"}


def clean_html(raw):
    """RSS summaries often contain HTML tags — strip them."""
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def call_hf(model, text, retries=2):
    url = config.HF_API_URL.format(model=model)
    payload = {"inputs": text[:1800], "options": {"wait_for_model": True}}

    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data and "summary_text" in data[0]:
                    return data[0]["summary_text"].strip()
                if isinstance(data, list) and data and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                logger.warning(f"Unexpected HF response shape: {str(data)[:200]}")
                return None
            elif resp.status_code == 503:
                # model loading (cold start) — wait and retry
                logger.info("HF model loading, retrying...")
                time.sleep(15)
                continue
            else:
                logger.warning(f"HF API error {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"HF request failed (attempt {attempt}): {e}")
            time.sleep(5)
    return None


def fallback_trim(text, max_words=45):
    """If AI summarization fails, fall back to a clean trimmed excerpt
    so the pipeline never breaks and pages never go empty."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(",.;:") + "..."


def summarize_item(item):
    raw_text = clean_html(item["raw_summary"]) or item["title"]
    source_text = f"{item['title']}. {raw_text}"

    # English summary
    summary_en = call_hf(config.HF_SUMMARIZER_EN, source_text)
    if not summary_en or len(summary_en.strip()) < 10:
        summary_en = fallback_trim(source_text)
        item["_en_fallback"] = True

    # Hindi summary (multilingual model can take English source and output Hindi-ish;
    # if it fails, we fall back to a trimmed English excerpt marked for manual review)
    summary_hi = call_hf(config.HF_SUMMARIZER_MULTI, source_text)
    if not summary_hi or len(summary_hi.strip()) < 10:
        summary_hi = None  # detector will flag this item for the Hindi edition
        item["_hi_fallback"] = True

    item["summary_en"] = summary_en
    item["summary_hi"] = summary_hi or ""
    item["summarized"] = True
    return item


def process_category(category):
    path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
    if not os.path.exists(path):
        return 0, 0

    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    processed, failed = 0, 0
    for item in items:
        if item.get("summarized"):
            continue
        try:
            summarize_item(item)
            processed += 1
        except Exception as e:
            logger.error(f"Failed to summarize item '{item.get('title','?')[:50]}': {e}")
            item["summary_en"] = fallback_trim(clean_html(item["raw_summary"]) or item["title"])
            item["summarized"] = True
            item["_error_fallback"] = True
            failed += 1
        time.sleep(1)  # be gentle on free-tier rate limits

    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return processed, failed


def run():
    logger.info("===== Summarize run started =====")
    total_processed, total_failed = 0, 0
    for category in config.RSS_SOURCES.keys():
        p, f = process_category(category)
        total_processed += p
        total_failed += f
    logger.info(f"===== Summarize run finished: {total_processed} processed, {total_failed} used fallback =====")
    print(f"Summarize complete: {total_processed} items processed ({total_failed} used fallback text).")


if __name__ == "__main__":
    run()
