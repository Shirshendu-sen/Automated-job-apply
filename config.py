# config.py
# ─────────────────────────────────────────────────────────────────────────────
# SEARCH CRITERIA
# ─────────────────────────────────────────────────────────────────────────────

# ── What kind of job are you looking for? ─────────────────────────────────────
SEARCH_KEYWORDS = (
    '"Full Stack Developer" OR '
    '"Backend Developer" OR '
    '"Software Engineer" OR '
    '"Python Developer" OR '
    '"Node.js Developer" OR '
    '"Next.js Developer" OR '
    '"React Developer" OR '
    '"AI Engineer" OR '
    '"Generative AI Engineer"'
)

# ── Search Locations ──────────────────────────────────────────────────────────
SEARCH_LOCATION = "Remote, Bangalore, Hyderabad, Pune, Chennai, Noida, Gurgaon"

# ── Job Freshness Filter ─────────────────────────────────────────────────────
# Options:
# "24h" = last 24 hours
# "3d"  = last 3 days
# "7d"  = last 7 days
# "30d" = last 30 days
# "any" = no filter

JOB_POSTED_WITHIN = "7d"

# ── Experience range ──────────────────────────────────────────────────────────
MIN_EXPERIENCE_YEARS = 0
MAX_EXPERIENCE_YEARS = 3

# ── Work mode filter ──────────────────────────────────────────────────────────
# Options:
# "remote", "hybrid", "onsite", "any"
WORK_MODE_FILTER = "any"

# ── Salary filter ─────────────────────────────────────────────────────────────
MIN_SALARY_LPA = 6

# ── AI relevance threshold ────────────────────────────────────────────────────
# Higher = safer and more relevant applications
MIN_RELEVANCE_SCORE = 70

# ── Daily limits per platform ─────────────────────────────────────────────────
# Safe initial limits
DAILY_LIMITS = {
    "naukri":    20,
    "linkedin":  10,
    "indeed":    15,
    "instahyre": 10,
}

# ── Delay between applications (seconds) ──────────────────────────────────────
DELAY_MIN_SECONDS = 10
DELAY_MAX_SECONDS = 30

# ── Gap between platforms (seconds) ───────────────────────────────────────────
PLATFORM_GAP_MIN = 300
PLATFORM_GAP_MAX = 600

# ── Active platforms ──────────────────────────────────────────────────────────
# Platforms run sequentially (NOT simultaneously)

ACTIVE_PLATFORMS = [
    "naukri",
    "indeed",
    "instahyre"
]

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Options:
# "claude"
# "openai"
# "gemini"
# "openrouter"
# "agentrouter"

LLM_PROVIDER = "gemini"

# ── LLM Models ────────────────────────────────────────────────────────────────
LLM_MODELS = {

    # Claude
    "claude":        "claude-sonnet-4-20250514",
    "claude_fast":   "claude-haiku-4-5-20251001",

    # OpenAI
    "openai":        "gpt-4o",

    # Gemini
    "gemini":        "gemini-2.5-flash",

    # OpenRouter
    "openrouter":    "google/gemma-4-26b-a4b-it:free",

    # AgentRouter
    "agentrouter":   "claude-haiku-4-5-20251001",
}

# ── Run mode ──────────────────────────────────────────────────────────────────
# Options:
# "safe"
# "aggressive"
# "startup"
# "fresher"
# "remote"

RUN_MODE = "safe"

# ── Browser visibility ────────────────────────────────────────────────────────
# False = visible browser (recommended initially)
# True  = hidden/headless browser

HEADLESS = False

# ── Retry settings ────────────────────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10

# ── Human approval mode ───────────────────────────────────────────────────────
# True  = shortlist first, manual approval before apply
# False = fully automatic apply

HUMAN_APPROVAL_MODE = True

# ── Logging & debugging ───────────────────────────────────────────────────────
ENABLE_SCREENSHOTS = True
ENABLE_DEBUG_LOGS = True

# ── Resume variants ───────────────────────────────────────────────────────────
RESUME_MAP = {
    "backend":   "resume/Resume.pdf",
    "fullstack": "resume/Resume.pdf",
    "ai":        "resume/Resume.pdf",
    "default":   "resume/Resume.pdf",
}