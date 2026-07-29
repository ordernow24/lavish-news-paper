"""
LAVISH NEWS PAPER — PDF Generator
Din bhar collect + summarize + recheck hui news ko leke
16-page professional newspaper PDF banata hai — English aur Hindi, alag-alag.
Real newspaper jaisa 2-column layout, rules, category tags, page numbers.
"""

import json
import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepInFrame
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable
import config

PAGE_W, PAGE_H = A4
COL_GAP = 6 * mm
MARGIN = 14 * mm
COL_WIDTH = (PAGE_W - 2 * MARGIN - COL_GAP) / 2.0

logging.basicConfig(
    filename=config.LOG_FILE, level=logging.INFO,
    format="%(asctime)s [PDF] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "en": {
        "national": "NATIONAL", "politics": "POLITICS", "state": "STATE NEWS",
        "business": "BUSINESS", "sports": "SPORTS", "entertainment": "ENTERTAINMENT",
        "technology": "TECHNOLOGY", "editorial": "EDITORIAL & OPINION",
    },
    "hi": {
        "national": "राष्ट्रीय", "politics": "राजनीति", "state": "राज्य समाचार",
        "business": "व्यापार", "sports": "खेल", "entertainment": "मनोरंजन",
        "technology": "तकनीक", "editorial": "संपादकीय",
    },
}


def register_fonts():
    """Register Devanagari font if available; fall back to Helvetica for English.
    Font file expected at fonts/NotoSansDevanagari-Regular.ttf (download step in CI)."""
    hindi_font_path = os.path.join(config.FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
    hindi_bold_path = os.path.join(config.FONTS_DIR, "NotoSansDevanagari-Bold.ttf")
    if os.path.exists(hindi_font_path):
        pdfmetrics.registerFont(TTFont("Hindi", hindi_font_path))
        pdfmetrics.registerFont(TTFont("Hindi-Bold", hindi_bold_path if os.path.exists(hindi_bold_path) else hindi_font_path))
        return True
    logger.warning("Hindi font not found — Hindi PDF will fail gracefully / use fallback.")
    return False


def load_all_items():
    all_items = {}
    for category in config.RSS_SOURCES.keys():
        path = os.path.join(config.DATA_PENDING_DIR, f"{category}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
            # sort: highest-weight sources first, then newest
            items.sort(key=lambda x: (x.get("weight", 3), x.get("collected_at", "")))
            all_items[category] = items
        else:
            all_items[category] = []
    return all_items


def get_styles(lang, hindi_available):
    styles = getSampleStyleSheet()
    base_font = "Hindi" if (lang == "hi" and hindi_available) else "Helvetica"
    bold_font = "Hindi-Bold" if (lang == "hi" and hindi_available) else "Helvetica-Bold"
    # Serif headline font gives a classic newspaper feel for English; Hindi keeps Hind (no serif Devanagari bundled)
    headline_font = "Times-Bold" if lang == "en" else bold_font
    headline_font_big = "Times-Bold" if lang == "en" else bold_font

    custom = {
        "Masthead": ParagraphStyle("Masthead", fontName=headline_font, fontSize=34,
                                    textColor=colors.HexColor(config.COLOR_NAVY), alignment=1, spaceAfter=1, leading=38),
        "Tagline": ParagraphStyle("Tagline", fontName=base_font, fontSize=9.5,
                                   textColor=colors.HexColor(config.COLOR_GOLD), alignment=1, spaceAfter=3),
        "DateLine": ParagraphStyle("DateLine", fontName=base_font, fontSize=8.5,
                                    textColor=colors.black, alignment=1, spaceAfter=4),
        "SectionHeader": ParagraphStyle("SectionHeader", fontName=bold_font, fontSize=13,
                                         textColor=colors.white, backColor=colors.HexColor(config.COLOR_NAVY),
                                         alignment=0, spaceAfter=6, leftIndent=6, spaceBefore=0,
                                         borderPadding=(5, 6, 5, 6)),
        "Headline": ParagraphStyle("Headline", fontName=headline_font, fontSize=11.5,
                                    textColor=colors.HexColor(config.COLOR_NAVY), spaceAfter=2, spaceBefore=6, leading=14),
        "TopHeadline": ParagraphStyle("TopHeadline", fontName=headline_font_big, fontSize=22,
                                       textColor=colors.HexColor(config.COLOR_NAVY), spaceAfter=5, leading=26),
        "Body": ParagraphStyle("Body", fontName=base_font, fontSize=8.7,
                                textColor=colors.HexColor("#1a1a1a"), spaceAfter=3, leading=11.8, alignment=4),
        "Source": ParagraphStyle("Source", fontName=base_font, fontSize=7,
                                  textColor=colors.grey, spaceAfter=9),
        "AdBox": ParagraphStyle("AdBox", fontName=bold_font, fontSize=12,
                                 textColor=colors.HexColor(config.COLOR_NAVY), alignment=1, spaceAfter=6),
        "AdSub": ParagraphStyle("AdSub", fontName=base_font, fontSize=9,
                                 textColor=colors.black, alignment=1, spaceAfter=4),
        "PageNum": ParagraphStyle("PageNum", fontName=base_font, fontSize=8,
                                   textColor=colors.grey, alignment=1),
    }
    return custom


def make_page_decorator(brand_name, lang):
    """Draws a thin footer rule + page number + brand name on every page,
    like a real newspaper's running footer."""
    def _decorate(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(config.COLOR_GOLD))
        canvas.setLineWidth(0.6)
        y = 12 * mm
        canvas.line(MARGIN, y, PAGE_W - MARGIN, y)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        page_label = f"{brand_name}  •  Page {doc.page}"
        canvas.drawCentredString(PAGE_W / 2.0, y - 6, page_label)
        canvas.restoreState()
    return _decorate


def ad_banner_flowable(styles, lang):
    text_ad = {
        "en": ["YOUR AD COULD BE HERE", f"Contact: {config.CONTACT_PHONE}  |  {config.CONTACT_EMAIL}", config.AD_RATES_NOTE],
        "hi": ["यहां आपका विज्ञापन हो सकता है", f"संपर्क करें: {config.CONTACT_PHONE}  |  {config.CONTACT_EMAIL}", "दरों के लिए संपर्क करें"],
    }[lang]
    t = Table(
        [[Paragraph(text_ad[0], styles["AdBox"])],
         [Paragraph(text_ad[1], styles["AdSub"])],
         [Paragraph(text_ad[2], styles["AdSub"])]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(config.COLOR_GOLD)),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEF")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def masthead_flowable(styles, lang, edition_date):
    name = config.BRAND_NAME_HI if lang == "hi" else config.BRAND_NAME_EN
    tagline = config.TAGLINE_HI if lang == "hi" else config.TAGLINE_EN
    left_tag = "Vol. 1  |  Daily Digital Edition" if lang == "en" else "वर्ष 1 | दैनिक डिजिटल संस्करण"
    right_tag = "Free Edition" if lang == "en" else "मुफ़्त संस्करण"
    strip = Table(
        [[Paragraph(left_tag, styles["DateLine"]),
          Paragraph(edition_date, styles["DateLine"]),
          Paragraph(right_tag, styles["DateLine"])]],
        colWidths=[(PAGE_W - 2 * MARGIN) / 3.0] * 3,
    )
    strip.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elems = [
        HRFlowable(width="100%", thickness=0.6, color=colors.grey),
        Spacer(1, 2),
        strip,
        Paragraph(name, styles["Masthead"]),
        Paragraph(tagline, styles["Tagline"]),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor(config.COLOR_NAVY)),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(config.COLOR_GOLD)),
        Spacer(1, 8),
    ]
    return elems


def category_tag(label, styles):
    return Paragraph(f'<font color="{config.COLOR_GOLD}" size=7.5><b>{label}</b></font>', styles["Source"])


def news_block(item, styles, lang, big=False, tag_label=None):
    title = item["title"]
    summary = item["summary_hi"] if lang == "hi" and item.get("summary_hi") else item["summary_en"]
    source = item["source"]
    elems = []
    if tag_label:
        elems.append(category_tag(tag_label, styles))
    elems.append(Paragraph(title, styles["TopHeadline"] if big else styles["Headline"]))
    elems.append(HRFlowable(width="35%" if not big else "100%", thickness=0.7,
                             color=colors.HexColor(config.COLOR_GOLD), spaceAfter=3, hAlign="LEFT"))
    elems.append(Paragraph(summary, styles["Body"]))
    elems.append(Paragraph("— " + source, styles["Source"]))
    return elems


def two_column_table(left_flowables, right_flowables):
    left_frame = KeepInFrame(COL_WIDTH, 250 * mm, left_flowables, mode="shrink")
    right_frame = KeepInFrame(COL_WIDTH, 250 * mm, right_flowables, mode="shrink")
    t = Table([[left_frame, right_frame]], colWidths=[COL_WIDTH, COL_WIDTH])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEAFTER", (0, 0), (0, 0), 0.6, colors.HexColor("#CCCCCC")),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), COL_GAP / 2.0),
        ("LEFTPADDING", (1, 0), (1, 0), COL_GAP / 2.0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def build_pdf(lang, all_items, edition_date, hindi_available):
    styles = get_styles(lang, hindi_available)
    filename = f"LAVISH_NEWS_{'HINDI' if lang=='hi' else 'ENGLISH'}_{edition_date}.pdf"
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                             topMargin=12 * mm, bottomMargin=20 * mm,
                             leftMargin=MARGIN, rightMargin=MARGIN)
    story = []
    used_ids = set()
    filler_pool = list(config.FILLER_CONTENT[lang])
    filler_idx = 0

    def get_items(category, n):
        nonlocal filler_idx
        pool = [i for i in all_items.get(category, []) if i["id"] not in used_ids]
        picked = pool[:n]
        for p in picked:
            used_ids.add(p["id"])
        # if short, pad with filler so the page is never empty
        while len(picked) < n and filler_idx < len(filler_pool):
            picked.append({
                "title": filler_pool[filler_idx]["title"] if lang == "en" else filler_pool[filler_idx]["title"],
                "summary_en": filler_pool[filler_idx]["summary"], "summary_hi": filler_pool[filler_idx]["summary"],
                "source": config.BRAND_NAME_EN if lang == "en" else config.BRAND_NAME_HI, "id": f"filler_{filler_idx}",
            })
            filler_idx += 1
        return picked

    for page_cfg in config.PAGE_LAYOUT:
        ptype = page_cfg["type"]

        if ptype == "front":
            story += masthead_flowable(styles, lang, edition_date)
            cat = page_cfg["categories"][0]
            label = CATEGORY_LABELS[lang][cat]
            items = get_items(cat, 3)
            if items:
                story += news_block(items[0], styles, lang, big=True, tag_label=label)
                story.append(Spacer(1, 4))
                if len(items) > 1:
                    left_col, right_col = [], []
                    for i, it in enumerate(items[1:3]):
                        target = left_col if i == 0 else right_col
                        target += news_block(it, styles, lang, tag_label=label)
                    story.append(two_column_table(left_col, right_col))

        elif ptype in ("content", "content_ad"):
            cat = page_cfg["categories"][0]
            label = CATEGORY_LABELS[lang][cat]
            story.append(Paragraph(f"  {label}", styles["SectionHeader"]))
            n = 4 if ptype == "content" else 2
            picked = get_items(cat, n)
            left_col, right_col = [], []
            for i, it in enumerate(picked):
                target = left_col if i % 2 == 0 else right_col
                target += news_block(it, styles, lang)
            if picked:
                story.append(two_column_table(left_col, right_col))
            if ptype == "content_ad":
                story.append(Spacer(1, 10))
                story.append(ad_banner_flowable(styles, lang))

        elif ptype == "full_ad":
            story.append(Spacer(1, 60))
            story.append(ad_banner_flowable(styles, lang))
            story.append(Spacer(1, 60))
            note = "This full page is reserved for advertisement" if lang == "en" else "यह पूरा पृष्ठ विज्ञापन के लिए आरक्षित है"
            story.append(Paragraph(note, styles["AdSub"]))

        elif ptype == "editorial":
            label = CATEGORY_LABELS[lang]["editorial"]
            story.append(Paragraph(f"  {label}", styles["SectionHeader"]))
            for it in get_items("editorial", 1):
                story += news_block(it, styles, lang, big=True)

        elif ptype == "back_ad":
            title = "ADVERTISE WITH US" if lang == "en" else "हमारे साथ विज्ञापन दें"
            story.append(Paragraph(title, styles["Masthead"]))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor(config.COLOR_GOLD)))
            story.append(Spacer(1, 12))
            story.append(ad_banner_flowable(styles, lang))
            story.append(Spacer(1, 14))
            contact_lines = [
                f"Phone / WhatsApp: {config.CONTACT_WHATSAPP}",
                f"Email: {config.CONTACT_EMAIL}",
                f"{config.AD_RATES_NOTE}",
            ] if lang == "en" else [
                f"फ़ोन / व्हाट्सएप: {config.CONTACT_WHATSAPP}",
                f"ईमेल: {config.CONTACT_EMAIL}",
                "दरों के लिए संपर्क करें",
            ]
            for line in contact_lines:
                story.append(Paragraph(line, styles["AdSub"]))

        story.append(PageBreak())

    decorator = make_page_decorator(config.BRAND_NAME_HI if lang == "hi" else config.BRAND_NAME_EN, lang)
    try:
        doc.build(story, onFirstPage=decorator, onLaterPages=decorator)
        logger.info(f"PDF built successfully: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"PDF build FAILED for {lang}: {e}")
        return None


def run():
    logger.info("===== PDF generation started =====")
    hindi_available = register_fonts()
    all_items = load_all_items()
    edition_date = datetime.now().strftime("%d-%b-%Y")

    results = {}
    results["en"] = build_pdf("en", all_items, edition_date, hindi_available)

    if hindi_available:
        results["hi"] = build_pdf("hi", all_items, edition_date, hindi_available)
    else:
        logger.warning("Skipping Hindi PDF — font missing. English PDF still generated.")
        results["hi"] = None

    logger.info(f"===== PDF generation finished: {results} =====")
    print(f"PDF generation done: {results}")
    return results


if __name__ == "__main__":
    run()
