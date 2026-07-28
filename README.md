# 📰 LAVISH NEWS PAPER — Automated Daily Digital Newspaper

Fully automated system: India news scrape → AI summarize (Hindi + English) →
16-page PDF → daily Telegram delivery at midnight. 100% free stack (GitHub Actions + Hugging Face free API + Telegram Bot).

---

## ⚠️ STEP 0 — Security (Do this first)

Aapne pehle jo tokens chat me share kiye the, unhe **regenerate karo** before going live:
- Telegram: `@BotFather` → `/mybots` → your bot → **API Token** → **Revoke current token**, naya token milega
- Hugging Face: huggingface.co/settings/tokens → purana token delete karo → naya banao

Kabhi bhi tokens ko code me hardcode mat karo ya chat/WhatsApp pe mat bhejo — hamesha GitHub Secrets me daalo (Step 3).

---

## STEP 1 — Repo Setup

```bash
git init lavish-news-paper
cd lavish-news-paper
# is folder ki saari files yahan copy karo
git add .
git commit -m "Initial commit: Lavish News Paper automation"
git branch -M main
git remote add origin https://github.com/<your-username>/lavish-news-paper.git
git push -u origin main
```

Repo **public** rakhna better hai (GitHub Actions minutes unlimited free milte hain public repos par).

---

## STEP 2 — Edit Your Details

`config.py` file kholo aur ye update karo:
- `CONTACT_PHONE`, `CONTACT_EMAIL`, `CONTACT_WHATSAPP` — apna real contact
- `AD_RATES_NOTE` — agar fixed rate batana hai
- `RSS_SOURCES` — koi source dead nikle to yahan se hata/badal do

---

## STEP 3 — Add Secrets on GitHub

Repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these 3 (naye/regenerated tokens):

| Secret Name | Value |
|---|---|
| `HF_API_TOKEN` | Hugging Face token |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram channel/chat ID |

**Important**: Bot ko apne Telegram channel me **Admin** banana zaroori hai, warna wo document send nahi kar payega.

---

## STEP 4 — Automation Already Configured

Do workflows already `.github/workflows/` me hain, koi extra setup nahi chahiye:

| Workflow | Kab chalta hai | Kya karta hai |
|---|---|---|
| `collect.yml` | Har 4 ghante (6AM, 10AM, 2PM, 6PM, 10PM IST) | Scrape → Summarize → Recheck |
| `publish.yml` | Raat 12:00 AM IST | Final recheck → PDF (EN+HI) → Telegram send → Archive |

Manual test ke liye: repo → **Actions** tab → workflow select karo → **Run workflow** button.

---

## STEP 5 — Test Locally (optional, before going live)

```bash
pip install -r requirements.txt
export HF_API_TOKEN="your_token"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_id"

python scripts/run_cycle.py      # scrape + summarize + recheck
python scripts/run_publish.py    # build PDFs + send to Telegram
```

PDFs `output/` folder me milenge.

---

## 🛡️ Built-in "Detector" (Error Recheck) — Kya Kya Check Hota Hai

- Duplicate news (same story do baar nahi jayegi)
- Broken/dead links skip
- Khali ya garbled summary skip
- Bahut lambi summary flag
- HF API fail ho to fallback trimmed text use hota hai (pipeline kabhi nahi rukta)
- Telegram send fail ho to 3 baar retry, phir admin ko alert message
- Har page ke liye minimum items na milein to filler content (Did You Know / Quote) use hota hai — page kabhi khali nahi dikhega

Sab logs `data/pipeline.log` me milte hain — GitHub Actions ke "logs" tab me bhi dikhega.

---

## 📁 Project Structure

```
lavish-news-paper/
├── config.py              # Saari settings, brand info, RSS sources
├── requirements.txt
├── scripts/
│   ├── scraper.py          # RSS collection
│   ├── summarizer.py       # Hugging Face AI summarization
│   ├── detector.py         # Quality/error recheck
│   ├── pdf_generator.py    # 16-page PDF builder (EN + HI)
│   ├── telegram_sender.py  # Delivery
│   ├── run_cycle.py        # 4-hourly orchestrator
│   └── run_publish.py      # Midnight orchestrator
├── data/
│   ├── pending/             # Today's collected news (auto-managed)
│   └── archive/             # Past days' data (auto-managed)
├── fonts/                   # Hindi font (auto-downloaded in CI)
├── output/                  # Generated PDFs
└── .github/workflows/       # Automation schedules
```

---

## 💡 Known Limitations (honest notes)

- Hugging Face **free** Inference API kabhi kabhi slow/cold-start hota hai — isliye fallback text logic already built-in hai
- Kuch news sites RSS allow nahi karte ya feed URL change karte rehte hain — agar koi source fail hone lage, `config.py` me se check/replace karna hoga
- 16 pages daily bharne ke liye achi khaasi news chahiye — agar kisi din kam mile to filler content page bharega, lekin real news hamesha priority me rahegi
