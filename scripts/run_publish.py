"""
LAVISH NEWS PAPER — Midnight Publish Runner
Raat 12 baje chalta hai: Final Recheck -> PDF (EN+HI) -> Telegram Send -> Archive & Reset
"""

import sys
import os
import json
import shutil
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import detector
import pdf_generator
import telegram_sender

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [PUBLISH] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def archive_and_reset():
    """Move today's used data into archive/, so tomorrow starts fresh (no duplicate carryover)."""
    today = datetime.now().strftime("%Y-%m-%d")
    archive_path = os.path.join(config.DATA_ARCHIVE_DIR, today)
    os.makedirs(archive_path, exist_ok=True)

    if os.path.exists(config.DATA_PENDING_DIR):
        for fname in os.listdir(config.DATA_PENDING_DIR):
            src = os.path.join(config.DATA_PENDING_DIR, fname)
            dst = os.path.join(archive_path, fname)
            try:
                shutil.copy2(src, dst)
                os.remove(src)
            except Exception as e:
                logger.error(f"Archive/reset failed for {fname}: {e}")
    logger.info(f"Archived today's data to {archive_path} and reset pending/")


def main():
    logger.info("########## MIDNIGHT PUBLISH START ##########")

    try:
        report = detector.run_recheck()
        logger.info(f"Final recheck report: ok={report['ok']} flagged={report['flagged']}")
    except Exception as e:
        logger.error(f"Final recheck crashed: {e}")

    pdf_paths = {"en": None, "hi": None}
    try:
        pdf_paths = pdf_generator.run()
    except Exception as e:
        logger.error(f"PDF generation crashed: {e}")

    try:
        telegram_sender.run(pdf_paths)
    except Exception as e:
        logger.error(f"Telegram send crashed: {e}")

    try:
        archive_and_reset()
    except Exception as e:
        logger.error(f"Archive/reset crashed: {e}")

    logger.info("########## MIDNIGHT PUBLISH END ##########")


if __name__ == "__main__":
    main()
