# 🤖 Job Bot — AI-Powered Automated Job Application Agent

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![browser-use](https://img.shields.io/badge/browser--use-0.12.6+-00ADD8?style=for-the-badge&logo=googlechrome&logoColor=white)](https://github.com/browser-use/browser-use)
[![LLM](https://img.shields.io/badge/LLM-Claude%20|%20GPT%20|%20Gemini-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)](#-llm-providers)
[![Platforms](https://img.shields.io/badge/Platforms-4-FF6B35?style=for-the-badge&logo=linkedin&logoColor=white)](#-supported-platforms)

**An AI agent that navigates job portals, reads descriptions, evaluates relevance, and applies — all on autopilot.**

</div>

---

## 📖 Table of Contents

- [🎯 What It Does](#-what-it-does)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [⚡ Quick Start](#-quick-start)
- [⚙️ Configuration](#️-configuration)
- [🎛️ Run Modes](#️-run-modes)
- [🌐 Supported Platforms](#-supported-platforms)
- [🧠 LLM Providers](#-llm-providers)
- [🧪 Testing & Validation](#-testing--validation)
- [📊 Tracking & Logging](#-tracking--logging)
- [🛡️ Scaling Safely](#️-scaling-safely)
- [🔧 Troubleshooting](#-troubleshooting)
- [📋 Quick Start Checklist](#-quick-start-checklist)
- [📄 File Reference](#-file-reference)

---

## 🎯 What It Does

```
┌─────────────────────────────────────────────────────────────────┐
│                        JOB BOT PIPELINE                         │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Naukri  │    │ LinkedIn │    │  Indeed  │    │Instahyre │  │
│  │  .com    │───▶│  .com    │───▶│  .in     │───▶│  .com    │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │        │
│       └───────────────┴───────────────┴───────────────┘        │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │  SQLite DB  │   ◀── Tracks every application│
│                    │  Tracker    │       with dedup detection    │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │  Daily      │                              │
│                    │  Report     │                              │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

The bot launches a **persistent Chrome browser session**, logs into job portals once (manual login), then on every subsequent run it's already authenticated. It reads your profile, searches across platforms, evaluates job descriptions against your skills using an LLM, and either:

| Mode | Behavior |
|------|----------|
| 🔍 **Human Approval** (`HUMAN_APPROVAL_MODE = True`) | Shortlists jobs for your review — prints `SHORTLISTED:` with job details |
| 🚀 **Auto Apply** (`HUMAN_APPROVAL_MODE = False`) | Applies automatically — prints `APPLIED:` / `SKIPPED:` with reasons |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                           config.py                                   │
│   Keywords • Location • Limits • LLM Provider • Run Mode • Delays    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌────────────────┐   ┌────────────────┐   ┌──────────────────────┐
│   profile.py   │   │   main.py      │   │   agents/base.py     │
│                │   │                │   │                      │
│  Name, Email,  │   │  daily_run()   │   │  get_llm()           │
│  Skills, Exp,  │──▶│  ──────────    │──▶│  build_compact_      │
│  Resume, CTC   │   │  parse_and_    │   │  prompt()            │
│                │   │  log()         │   │  run_agent()         │
└────────────────┘   └───────┬────────┘   └──────────┬───────────┘
                             │                        │
                             ▼                        ▼
                    ┌────────────────┐    ┌──────────────────────┐
                    │  tracker.py    │    │    modes/             │
                    │                │    │                       │
                    │  SQLite DB     │    │  safe · aggressive    │
                    │  Partial       │    │  startup · fresher    │
                    │  Unique Index  │    │  remote               │
                    └────────────────┘    └──────────────────────┘
```

### Data Flow

```
search keywords ──→ build_compact_prompt() ──→ Agent.run() ──→ browser actions
                                                        │
                                              ┌─────────▼─────────┐
                                              │  APPLIED: [title]  │
                                              │  SKIPPED: [title]  │
                                              │  SHORTLISTED: [...]│
                                              └─────────┬─────────┘
                                                        ▼
                                              parse_and_log() ──→ SQLite
```

---

## 📁 Project Structure

```
job-bot/
│
├── main.py              🔵 Entry point — orchestrates the daily run
├── config.py            🟡 All search criteria & operational settings
├── profile.py           🟢 Your personal profile (skills, resume, CTC)
├── tracker.py           🟣 SQLite application tracker with dedup
├── pyproject.toml       📦 Dependencies (browser-use, playwright, etc.)
│
├── agents/              🧠 Platform-specific AI agents
│   ├── __init__.py
│   ├── base.py          ⭐ Universal runner + LLM factory + compact prompt
│   ├── naukri.py        🇮🇳 Naukri.com agent (legacy standalone)
│   ├── linkedin.py      💼 LinkedIn agent (legacy standalone)
│   ├── indeed.py        🔍 Indeed India agent (legacy standalone)
│   └── instahyre.py     🚀 Instahyre agent (legacy standalone)
│
├── modes/               🎛️ Prompt injection strategies
│   ├── __init__.py
│   ├── safe.py          🛡️ Conservative — high relevance threshold
│   ├── aggressive.py    ⚡ Maximum volume — low threshold
│   ├── startup.py       🏢 Product startups only
│   ├── fresher.py       🎓 Entry-level / 0-2 years
│   └── remote.py        🏠 Remote / WFH only
│
├── logs/                📊 Runtime output
│   ├── applications.db  🗄️ SQLite tracking database
│   ├── screenshots/     📸 Agent conversation screenshots
│   └── run_*.log        📝 Daily run logs
│
├── browser_data/        🍪 Persistent Chrome profile (login cookies)
├── resume/              📄 Your resume PDF(s)
│
├── test_setup.py        ✅ Setup verification (API, browser, DB)
├── login_setup.py       🔑 One-time manual login for all platforms
├── dry_run_test.py      🧪 Comprehensive 6-step QA test
├── run_checks.py        🔍 Static validation (imports, config, profile)
└── .env                 🔐 API keys (never committed)
```

---

## ⚡ Quick Start

### 1. Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.11+ | `python --version` |
| uv (package manager) | latest | `uv --version` |
| Google Chrome | any recent | Installed |
| LLM API Key | — | See [LLM Providers](#-llm-providers) |

### 2. Clone & Install

```bash
# Clone the repository
git clone <repo-url> job-bot
cd job-bot

# Install dependencies with uv
uv sync
uv run playwright install chromium
```

### 3. Create Your `.env` File

```env
# ── Choose ONE provider ──────────────────────────────
GOOGLE_API_KEY=your_gemini_api_key_here
# ANTHROPIC_API_KEY=sk-ant-...      (if using Claude)
# OPENAI_API_KEY=sk-...             (if using OpenAI)
# OPENROUTER_API_KEY=sk-or-...      (if using OpenRouter)
# AGENTROUTER_API_KEY=ar-...        (if using AgentRouter)
```

### 4. Fill In Your Profile

Edit [`profile.py`](job-bot/profile.py) with your:
- Name, email, phone
- Skills (primary & secondary)
- Experience, current CTC, expected CTC
- Resume path
- Target roles & locations

### 5. Place Your Resume

```bash
# Put your resume at:
job-bot/resume/Resume.pdf
```

### 6. Run Setup Tests

```bash
uv run python test_setup.py
```

Expected output:
```
  Browser-Use Setup Test
  ✓ API key validated
  ✓ Browser launched
  ✓ Chrome profile connected
  ✓ Profile file OK
  ✓ SQLite tracker OK
  Tests complete. Fix any ✗ errors before running main.py.
```

### 7. One-Time Login Setup

```bash
uv run python login_setup.py
```

This opens each platform in sequence (Naukri → LinkedIn → Indeed → Instahyre). **Log in manually** in each browser window and press Enter when done. Login cookies are saved in [`browser_data/`](job-bot/browser_data/) and reused on every subsequent run.

### 8. Run Static Checks

```bash
uv run python run_checks.py
```

### 9. Dry Run Test (Recommended)

```bash
uv run python dry_run_test.py
```

This runs a 6-step test with `max_steps=3` per platform — verifies the full pipeline without actually applying.

### 10. Run the Bot

```bash
# First run — watch it work (HEADLESS = False)
uv run python main.py

# Once confident, switch to headless in config.py
# HEADLESS = True
```

---

## ⚙️ Configuration

All settings live in [`config.py`](job-bot/config.py):

```python
# ── Search Criteria ────────────────────────────────────────
SEARCH_KEYWORDS   = '"Full Stack Developer" OR "Backend Developer" OR ...'
SEARCH_LOCATION   = "Remote, Bangalore, Hyderabad, Pune, ..."
JOB_POSTED_WITHIN = "7d"        # 24h | 3d | 7d | 30d | any
MIN_EXPERIENCE_YEARS = 0
MAX_EXPERIENCE_YEARS = 3
WORK_MODE_FILTER     = "any"    # remote | hybrid | onsite | any
MIN_SALARY_LPA       = 6
MIN_RELEVANCE_SCORE  = 70

# ── Daily Limits ──────────────────────────────────────────
DAILY_LIMITS = {
    "naukri":    20,
    "linkedin":  10,
    "indeed":    15,
    "instahyre": 10,
}

# ── Timing ─────────────────────────────────────────────────
DELAY_MIN_SECONDS = 10          # Between applications
DELAY_MAX_SECONDS = 30
PLATFORM_GAP_MIN  = 300         # Between platforms (5 min)
PLATFORM_GAP_MAX  = 600         # Between platforms (10 min)

# ── Active Platforms ──────────────────────────────────────
ACTIVE_PLATFORMS = ["naukri", "indeed", "instahyre"]

# ── LLM ───────────────────────────────────────────────────
LLM_PROVIDER = "gemini"         # claude | openai | gemini | openrouter | agentrouter
LLM_MODELS = {
    "gemini":   "gemini-2.5-flash",
    "claude":   "claude-sonnet-4-20250514",
    "openai":   "gpt-4o",
}

# ── Mode & Behavior ────────────────────────────────────────
RUN_MODE            = "safe"    # safe | aggressive | startup | fresher | remote
HEADLESS            = False     # True = hidden browser window
HUMAN_APPROVAL_MODE = True      # True = shortlist first | False = auto-apply

# ── Resume ─────────────────────────────────────────────────
RESUME_MAP = {
    "default": "resume/Resume.pdf",
}
```

---

## 🎛️ Run Modes

Modes inject filtering strategies into the agent prompt. Change `RUN_MODE` in [`config.py`](job-bot/config.py):

| Mode | File | Strategy | Min Relevance | Key Behavior |
|------|------|----------|:---:|-------------|
| 🛡️ **Safe** | [`modes/safe.py`](job-bot/modes/safe.py) | Conservative | **70** | ≥3 skill matches, mid-size companies, no interns/trainees |
| ⚡ **Aggressive** | [`modes/aggressive.py`](job-bot/modes/aggressive.py) | Maximum volume | **45** | ≥1 skill match, all company sizes, max daily limits |
| 🏢 **Startup** | [`modes/startup.py`](job-bot/modes/startup.py) | Product companies | **65** | Skips TCS/Infosys/Wipro, prefers SaaS & funded startups |
| 🎓 **Fresher** | [`modes/fresher.py`](job-bot/modes/fresher.py) | Entry-level | **50** | 0-2 years only, Junior/Graduate/Intern roles |
| 🏠 **Remote** | [`modes/remote.py`](job-bot/modes/remote.py) | WFH only | **60** | Remote/WFH only, hybrid OK, skips onsite-only |

---

## 🌐 Supported Platforms

| Platform | Agent File | Key Notes |
|----------|-----------|-----------|
| 🇮🇳 **Naukri** | [`agents/naukri.py`](job-bot/agents/naukri.py) | India's largest job portal. Close login popups. Use Easy Apply. |
| 💼 **LinkedIn** | [`agents/linkedin.py`](job-bot/agents/linkedin.py) | Aggressive bot detection. **Only Easy Apply jobs**. Skip external apply links. |
| 🔍 **Indeed** | [`agents/indeed.py`](job-bot/agents/indeed.py) | Indeed India. Use "Easily Apply" only. Skip "Apply on company site". |
| 🚀 **Instahyre** | [`agents/instahyre.py`](job-bot/agents/instahyre.py) | Product companies & startups focus. Use existing Chrome session. |

> ⚠️ **All platforms** now route through the universal [`run_agent()`](job-bot/agents/base.py) in `base.py`. The per-platform agent files (`naukri.py`, `linkedin.py`, etc.) contain legacy standalone functions that are no longer called by `main.py` — the universal [`build_compact_prompt()`](job-bot/agents/base.py) handles all platforms with ~60% fewer tokens.

---

## 🧠 LLM Providers

| Provider | Model | Cost Estimate | Setup |
|----------|-------|:---:|-------|
| **Gemini** | `gemini-2.5-flash` | 💲 Lowest | `GOOGLE_API_KEY` in `.env` |
| **Claude** | `claude-sonnet-4-20250514` | 💲💲 Medium | `ANTHROPIC_API_KEY` in `.env` |
| **OpenAI** | `gpt-4o` | 💲💲💲 Higher | `OPENAI_API_KEY` in `.env` |
| **OpenRouter** | Various | 💲 Varies | `OPENROUTER_API_KEY` in `.env` |
| **AgentRouter** | Various | 💲 Varies | `AGENTROUTER_API_KEY` in `.env` |

> 💡 **Recommendation**: Start with Gemini (`gemini-2.5-flash`) — lowest cost, good enough for job filtering. Switch to Claude or GPT-4o if you need more nuanced relevance evaluation.

---

## 🧪 Testing & Validation

### Setup Test
```bash
uv run python test_setup.py
```

Verifies: API key → Browser launch → Chrome profile → Profile fields → SQLite tracker

### Static Checks
```bash
uv run python run_checks.py
```

Verifies: All imports → .env/Config → Profile completeness → Tracker init → Prompt builder → LLM factory

### Dry Run
```bash
uv run python dry_run_test.py
```

6-step QA test per platform (max 3 steps):
1. **PRE-RUN guard** — checks config safety before starting
2. **Browser launch** — verifies persistent profile connects
3. **Login check** — confirms you're logged into each platform
4. **Agent dry-run** — runs with `max_steps=3`, no actual applications
5. **Shortlist format check** — validates output format
6. **Tracker log + Screenshot check** — verifies DB writes and screenshots

---

## 📊 Tracking & Logging

### SQLite Database

Schema at [`tracker.py`](job-bot/tracker.py):

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `job_title` | TEXT | Job title |
| `company` | TEXT | Company name |
| `platform` | TEXT | naukri / linkedin / indeed / instahyre |
| `status` | TEXT | applied / skipped / failed |
| `reason` | TEXT | Skip/fail reason |
| `job_url` | TEXT | Job URL (unique index on non-empty values) |
| `applied_at` | TEXT | ISO 8601 timestamp |

> 🛡️ **Duplicate protection**: Partial unique index on `job_url WHERE job_url IS NOT NULL AND job_url != ''`. Empty URLs never block each other.

### View Your Data

```bash
# Today's applications
uv run python -c "
from tracker import init_db, daily_report
conn = init_db()
for row in daily_report(conn):
    print(f'{row[0]:12} {row[1]:10} {row[2]} jobs')
"

# Total counts per platform
uv run python -c "
from tracker import init_db, all_time_report
conn = init_db()
for row in all_time_report(conn):
    print(f'{row[0]:12} {row[1]:10} {row[2]} jobs')
"
```

### Log Files

```
logs/
├── applications.db        # SQLite tracker
├── run_2025-05-24.log     # Daily run logs (timestamped)
└── screenshots/           # Agent step-by-step screenshots
```

---

## 🛡️ Scaling Safely

| Rule | Recommendation |
|------|---------------|
| 📊 **Daily Limits** | Start low (10–15/platform). Ramp up slowly over weeks. |
| ⏱️ **Delays** | 10–30s between applications. 5–10 min gap between platforms. |
| 🏠 **Home IP** | Run from your home IP. Avoid VPNs and corporate networks. |
| 🍪 **Real Profile** | Use your actual Chrome profile with genuine browsing history. |
| 📅 **Vary Schedule** | Don't run at exactly the same time every day. Add random offset. |
| 👀 **Monitor** | Check logs for CAPTCHAs, warnings, or blocks. Stop immediately if detected. |
| 🐢 **Ramp Up** | Week 1: 5–10 apps/day → Week 2: 15–20 → Week 3: 25–30 → Cap at 40–50. |

---

## 🔧 Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `AuthenticationError: Invalid API key` | Wrong/missing API key | Check `.env` file, verify key at provider dashboard |
| Browser launches & closes immediately | Chromium not installed | `uv run playwright install chromium` |
| `BrowserSession.from_system_chrome()` error | Chrome not found | Install Google Chrome or use bundled Chromium |
| `sqlite3.OperationalError: database is locked` | Concurrent access | Only one process should access the DB at a time |
| Bot gets stuck on a form field | Field selector changed | Add explicit selector hint in prompt |
| LinkedIn shows CAPTCHA | Bot-like behavior detected | Reduce frequency, use real Chrome profile, add delays |
| `TimeoutError` on a page | Slow page load | Add explicit wait instruction in prompt |

---

## 📋 Quick Start Checklist

```
☐ 1. Python 3.11+ installed
☐ 2. uv installed (pip install uv)
☐ 3. uv sync
☐ 4. uv run playwright install chromium
☐ 5. Create .env with API key
☐ 6. Fill in profile.py
☐ 7. Place resume at resume/Resume.pdf
☐ 8. Review config.py settings
☐ 9. uv run python test_setup.py        ← All ✓ ?
☐ 10. uv run python run_checks.py       ← All ✓ ?
☐ 11. uv run python login_setup.py      ← Login once manually
☐ 12. uv run python dry_run_test.py     ← QA gate
☐ 13. uv run python main.py             ← First real run!
```

---

## 📄 File Reference

| File | Purpose |
|------|---------|
| [`main.py`](job-bot/main.py) | Entry point — `daily_run()` orchestrator |
| [`config.py`](job-bot/config.py) | All search criteria, limits, LLM settings |
| [`profile.py`](job-bot/profile.py) | Your personal profile & resume path |
| [`tracker.py`](job-bot/tracker.py) | SQLite DB with partial unique index |
| [`agents/base.py`](job-bot/agents/base.py) | Universal runner, LLM factory, compact prompt |
| [`agents/naukri.py`](job-bot/agents/naukri.py) | Naukri agent (legacy standalone) |
| [`agents/linkedin.py`](job-bot/agents/linkedin.py) | LinkedIn agent (legacy standalone) |
| [`agents/indeed.py`](job-bot/agents/indeed.py) | Indeed agent (legacy standalone) |
| [`agents/instahyre.py`](job-bot/agents/instahyre.py) | Instahyre agent (legacy standalone) |
| [`modes/safe.py`](job-bot/modes/safe.py) | Safe mode instructions |
| [`modes/aggressive.py`](job-bot/modes/aggressive.py) | Aggressive mode instructions |
| [`modes/startup.py`](job-bot/modes/startup.py) | Startup mode instructions |
| [`modes/fresher.py`](job-bot/modes/fresher.py) | Fresher mode instructions |
| [`modes/remote.py`](job-bot/modes/remote.py) | Remote mode instructions |
| [`test_setup.py`](job-bot/test_setup.py) | Setup verification test |
| [`login_setup.py`](job-bot/login_setup.py) | One-time manual login helper |
| [`dry_run_test.py`](job-bot/dry_run_test.py) | 6-step QA dry run test |
| [`run_checks.py`](job-bot/run_checks.py) | Static validation checks |
| [`pyproject.toml`](job-bot/pyproject.toml) | Dependencies & project metadata |

---

<div align="center">

### ⚠️ Use Responsibly

This tool automates job applications. Respect platform rate limits, use realistic delays, and stop immediately if you receive warnings or CAPTCHAs. Run from your home IP with a genuine Chrome profile.

</div>