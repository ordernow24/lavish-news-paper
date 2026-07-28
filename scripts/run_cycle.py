"""
LAVISH NEWS PAPER — 4-Hourly Cycle Runner
GitHub Actions ye script har 4 ghante me chalata hai:
Scrape -> Summarize -> Detector Recheck
Kabhi bhi ek step fail ho to pura pipeline crash nahi hoga.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import scraper
import summarizer
import detector

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [CYCLE] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    os.makedirs(config.DATA_PENDING_DIR, exist_ok=True)
    logger.info("########## 4-HOURLY CYCLE START ##########")

    try:
        scraper.run()
    except Exception as e:
        logger.error(f"Scraper step crashed: {e}")

    try:
        summarizer.run()
    except Exception as e:
        logger.error(f"Summarizer step crashed: {e}")

    try:
        detector.run_recheck()
    except Exception as e:
        logger.error(f"Detector step crashed: {e}")

    logger.info("########## 4-HOURLY CYCLE END ##########")


if __name__ == "__main__":
    main()
