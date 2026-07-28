"""
LAVISH NEWS PAPER — Telegram Sender
Final PDFs (English + Hindi) ko Telegram channel pe bhejta hai.
Agar send fail ho to retry karta hai aur admin ko error alert bhejta hai.
"""

import os
import time
import logging
import requests
import config

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [TELEGRAM] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

API_BASE = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"


def send_document(filepath, caption, retries=3):
    if not os.path.exists(filepath):
        logger.error(f"Cannot send — file missing: {filepath}")
        return False

    url = f"{API_BASE}/sendDocument"
    for attempt in range(1, retries + 1):
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    url,
                    data={"chat_id": config.TELEGRAM_CHAT_ID, "caption": caption},
                    files={"document": f},
                    timeout=120,
                )
            if resp.status_code == 200 and resp.json().get("ok"):
                logger.info(f"Sent successfully: {filepath}")
                return True
            else:
                logger.warning(f"Send failed (attempt {attempt}): {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Send exception (attempt {attempt}): {e}")
        time.sleep(5)
    return False


def send_text_alert(message):
    """Used to notify the admin if something goes wrong in the pipeline."""
    try:
        url = f"{API_BASE}/sendMessage"
        requests.post(url, data={"chat_id": config.TELEGRAM_CHAT_ID, "text": message}, timeout=30)
    except Exception as e:
        logger.error(f"Failed to send alert message: {e}")


def run(pdf_paths: dict):
    logger.info("===== Telegram send started =====")
    results = {}

    if pdf_paths.get("en"):
        caption_en = f"📰 {config.BRAND_NAME_EN} — Daily English Edition"
        results["en"] = send_document(pdf_paths["en"], caption_en)
    else:
        results["en"] = False
        logger.error("English PDF missing — nothing sent.")

    if pdf_paths.get("hi"):
        caption_hi = f"📰 {config.BRAND_NAME_HI} — दैनिक हिंदी संस्करण"
        results["hi"] = send_document(pdf_paths["hi"], caption_hi)
    else:
        results["hi"] = False
        logger.warning("Hindi PDF missing — nothing sent for Hindi edition.")

    if not results["en"] and not results["hi"]:
        send_text_alert("⚠️ LAVISH NEWS PAPER: Aaj dono editions (Hindi + English) send fail ho gaye. Please check GitHub Actions logs.")

    logger.info(f"===== Telegram send finished: {results} =====")
    print(f"Telegram send results: {results}")
    return results


if __name__ == "__main__":
    from pdf_generator import run as generate_pdfs
    pdfs = generate_pdfs()
    run(pdfs)
