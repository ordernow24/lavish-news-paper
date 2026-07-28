"""
LAVISH NEWS PAPER — Central Configuration
Manager Notes: Saari settings yahin se control hoti hain.
Agar koi RSS source dead ho jaye, bas yahan URL change/remove karo.
"""

import os

# ============================================================
# BRAND
# ============================================================
BRAND_NAME_EN = "LAVISH NEWS PAPER"
BRAND_NAME_HI = "लविश न्यूज़ पेपर"
TAGLINE_EN = "News That Matters, Delivered With Class"
TAGLINE_HI = "सच, सटीक, शानदार"

COLOR_NAVY = "#0A1F44"
COLOR_GOLD = "#C9A227"
COLOR_BLACK = "#111111"

# ============================================================
# CONTACT / AD INFO (Manager: apna real contact yahan daalo)
# ============================================================
CONTACT_PHONE = "+91-XXXXXXXXXX"
CONTACT_EMAIL = "ads@lavishnewspaper.in"
CONTACT_WHATSAPP = "+91-XXXXXXXXXX"
AD_RATES_NOTE = "Contact for latest advertisement rates"

# ============================================================
# SECRETS (from GitHub Secrets / environment variables — never hardcode)
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")

# ============================================================
# HUGGING FACE MODELS
# ============================================================
HF_SUMMARIZER_EN = "facebook/bart-large-cnn"
HF_SUMMARIZER_MULTI = "csebuetnlp/mT5_multilingual_XLSum"  # good for Hindi
HF_API_URL = "https://api-inference.huggingface.co/models/{model}"

# ============================================================
# RSS SOURCES (India-focused, high-weightage / authoritative)
# weight: 1 = highest authority (govt/wire), 2 = high credibility, 3 = supporting
# ============================================================
RSS_SOURCES = {
    "national": [
        {"name": "PIB (Govt of India)", "url": "https://www.pib.gov.in/ViewRss.aspx?reg=1&lang=1", "weight": 1},
        {"name": "The Hindu - National", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "weight": 2},
        {"name": "NDTV - India News", "url": "https://feeds.feedburner.com/ndtvnews-india-news", "weight": 2},
    ],
    "politics": [
        {"name": "The Hindu - Politics", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "weight": 2},
        {"name": "NDTV - India News", "url": "https://feeds.feedburner.com/ndtvnews-india-news", "weight": 2},
    ],
    "state": [
        {"name": "The Hindu - Other States", "url": "https://www.thehindu.com/news/other-states/feeder/default.rss", "weight": 2},
        {"name": "NDTV - Cities", "url": "https://feeds.feedburner.com/ndtvnews-cities", "weight": 2},
    ],
    "business": [
        {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rssfeedsdefault.cms", "weight": 2},
        {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml", "weight": 2},
        {"name": "Business Standard", "url": "https://www.business-standard.com/rss/latest.rss", "weight": 2},
    ],
    "sports": [
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml", "weight": 2},
        {"name": "The Hindu - Sport", "url": "https://www.thehindu.com/sport/feeder/default.rss", "weight": 2},
        {"name": "NDTV Sports", "url": "https://feeds.feedburner.com/ndtvsports-latest", "weight": 2},
    ],
    "entertainment": [
        {"name": "The Hindu - Entertainment", "url": "https://www.thehindu.com/entertainment/feeder/default.rss", "weight": 2},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/rss/news.xml", "weight": 3},
    ],
    "technology": [
        {"name": "Gadgets360", "url": "https://www.gadgets360.com/rss/news", "weight": 2},
        {"name": "Economic Times Tech", "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", "weight": 2},
    ],
    "editorial": [
        {"name": "The Hindu - Editorial", "url": "https://www.thehindu.com/opinion/editorial/feeder/default.rss", "weight": 2},
    ],
}

# ============================================================
# CATEGORY -> PAGE MAPPING (16-page layout)
# ============================================================
PAGE_LAYOUT = [
    {"page": 1, "type": "front", "categories": ["national"]},
    {"page": 2, "type": "content", "categories": ["national"]},
    {"page": 3, "type": "content_ad", "categories": ["national"]},
    {"page": 4, "type": "content", "categories": ["state"]},
    {"page": 5, "type": "content", "categories": ["politics"]},
    {"page": 6, "type": "content_ad", "categories": ["politics"]},
    {"page": 7, "type": "content", "categories": ["business"]},
    {"page": 8, "type": "content", "categories": ["business"]},
    {"page": 9, "type": "full_ad", "categories": []},
    {"page": 10, "type": "content", "categories": ["sports"]},
    {"page": 11, "type": "content_ad", "categories": ["sports"]},
    {"page": 12, "type": "content", "categories": ["entertainment"]},
    {"page": 13, "type": "content", "categories": ["entertainment"]},
    {"page": 14, "type": "content", "categories": ["technology"]},
    {"page": 15, "type": "editorial", "categories": ["editorial"]},
    {"page": 16, "type": "back_ad", "categories": []},
]

# Minimum items needed per category to fill pages without looking empty
MIN_ITEMS_PER_CATEGORY = {
    "national": 8, "politics": 4, "state": 4, "business": 6,
    "sports": 6, "entertainment": 4, "technology": 4, "editorial": 1,
}

# ============================================================
# PATHS
# ============================================================
DATA_PENDING_DIR = "data/pending"
DATA_ARCHIVE_DIR = "data/archive"
OUTPUT_DIR = "output"
FONTS_DIR = "fonts"
LOG_FILE = "data/pipeline.log"

# Filler content used ONLY if a category falls short, so a page is never left blank
FILLER_CONTENT = {
    "en": [
        {"title": "Did You Know?", "summary": "India is home to over 19,500 languages and dialects spoken across its states — the most linguistically diverse nation in the world."},
        {"title": "Quote of the Day", "summary": "\"The best way to find yourself is to lose yourself in the service of others.\" — Mahatma Gandhi"},
    ],
    "hi": [
        {"title": "क्या आप जानते हैं?", "summary": "भारत में 19,500 से अधिक भाषाएं और बोलियां बोली जाती हैं — यह इसे विश्व का सबसे भाषाई रूप से विविध देश बनाता है।"},
        {"title": "आज का विचार", "summary": "\"स्वयं को खोजने का सबसे अच्छा तरीका है, स्वयं को दूसरों की सेवा में खो देना।\" — महात्मा गांधी"},
    ],
}
