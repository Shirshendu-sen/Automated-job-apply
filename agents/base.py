# agents/base.py
# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers used by all agent files.
# Centralized LLM provider configuration.
# Uses browser-use's own LLM classes (which have the required
# `provider`, `name`, `model_name` attributes) instead of langchain.
# ─────────────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """
    Returns the configured LLM instance.

    Supported providers:
    - claude
    - openai
    - gemini
    - openrouter
    - agentrouter
    """

    import os
    from config import LLM_PROVIDER, LLM_MODELS

    # ─────────────────────────────────────────────────────────────────────────
    # CLAUDE
    # ─────────────────────────────────────────────────────────────────────────
    if LLM_PROVIDER == "claude":

        from browser_use.llm.anthropic.chat import ChatAnthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in .env"
            )

        return ChatAnthropic(
            model=LLM_MODELS["claude"],
            api_key=api_key,
            temperature=0.2,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # OPENAI
    # ─────────────────────────────────────────────────────────────────────────
    elif LLM_PROVIDER == "openai":

        from browser_use.llm.openai.chat import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in .env"
            )

        return ChatOpenAI(
            model=LLM_MODELS["openai"],
            api_key=api_key,
            temperature=0.2,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # GEMINI
    # ─────────────────────────────────────────────────────────────────────────
    elif LLM_PROVIDER == "gemini":

        from browser_use.llm.google.chat import ChatGoogle

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in .env"
            )

        return ChatGoogle(
            model=LLM_MODELS["gemini"],
            api_key=api_key,
            temperature=0.0,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # OPENROUTER
    # ─────────────────────────────────────────────────────────────────────────
    elif LLM_PROVIDER == "openrouter":

        # OpenRouter provides OpenAI-compatible routing
        # for many models.

        from browser_use.llm.openai.chat import ChatOpenAI

        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in .env"
            )

        return ChatOpenAI(
            model=LLM_MODELS["openrouter"],
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=0.2,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # AGENTROUTER
    # ─────────────────────────────────────────────────────────────────────────
    elif LLM_PROVIDER == "agentrouter":

        # AgentRouter provides OpenAI-compatible routing
        # for multiple models.

        from browser_use.llm.openai.chat import ChatOpenAI

        api_key = os.getenv("AGENTROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "AGENTROUTER_API_KEY not found in .env"
            )

        return ChatOpenAI(
            model=LLM_MODELS["agentrouter"],
            base_url="https://agentrouter.org",
            api_key=api_key,
            temperature=0.2,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # INVALID PROVIDER
    # ─────────────────────────────────────────────────────────────────────────
    else:

        raise ValueError(
            f"Unknown LLM_PROVIDER: '{LLM_PROVIDER}'. "
            "Valid providers are: "
            "'claude', 'openai', 'gemini', "
            "'openrouter', 'agentrouter'"
        )


def build_compact_prompt(profile: dict, platform: str, limit: int,
                          search_kw: str, location: str,
                          delay_min: int, delay_max: int,
                          posted_within: str, approval_mode: bool,
                          mode_instructions: str = "") -> str:
    """
    Ultra-compact universal prompt. ~60% fewer tokens than platform-specific prompts.
    Works on Naukri, LinkedIn, Indeed, Instahyre.
    """

    skills     = ",".join(profile["primary_skills"][:6])   # top 6 only
    blacklist  = ",".join(profile["blacklisted_companies"]) or "none"
    exp        = profile["experience_years"]
    freshness  = "1d" if posted_within == "24h" else "7d"

    PLATFORM_URLS = {
        "naukri":    "https://www.naukri.com",
        "linkedin":  "https://www.linkedin.com/jobs/search/",
        "indeed":    "https://in.indeed.com",
        "instahyre": "https://www.instahyre.com",
    }
    if platform not in PLATFORM_URLS:
        raise ValueError(
            f"Unknown platform: '{platform}'. Valid platforms: "
            f"{', '.join(sorted(PLATFORM_URLS.keys()))}"
        )
    url = PLATFORM_URLS[platform]

    PLATFORM_HINTS = {
        "naukri":    "Close login popup if shown. Use Easy Apply button.",
        "linkedin":  "Must be logged in. Only Easy Apply jobs. Skip external Apply.",
        "indeed":    "Use Easily Apply only. Skip 'Apply on company site'.",
        "instahyre": "Use existing Chrome session. Do not create new account.",
    }
    hint = PLATFORM_HINTS.get(platform, "")

    apply_block = f"""
SHORTLIST only. Print per job:
SHORTLISTED: [title] at [company]
URL: [url]
""" if approval_mode else f"""
Auto-apply if relevant. Fill:
Name={profile['name']} Email={profile['email']} Phone={profile['phone']}
Exp={exp}y CTC={profile['current_ctc']} Expected={profile['expected_ctc']} Notice={profile['notice_period']}
Resume={profile['resume_path']}
Cover={profile['cover_letter_summary'][:120]}...
Print: APPLIED/SKIPPED: [title] at [company] — [reason]
"""

    return f"""Job agent for {profile['name']} on {platform.title()}.
{mode_instructions}
{hint}

GO TO: {url}
SEARCH: "{search_kw}" in "{location}"
FILTERS: exp={exp}y salary>={profile['min_salary_lpa']}LPA posted<{freshness} remote/hybrid preferred

SKIP IF: exp>{exp+2}y | no skill match({skills}) | company in({blacklist}) | BPO/support/sales/testing/non-tech

APPLY FLOW:
{apply_block}
PACE: wait {delay_min}-{delay_max}s between jobs
STOP: after {limit} jobs or 5 pages
END: print "Total shortlisted:X applied:Y skipped:Z"
"""


async def run_agent(platform: str, browser, mode_instructions: str = ""):
    """
    Single universal runner. Replaces apply_naukri / apply_linkedin /
    apply_indeed / apply_instahyre.
    """
    from browser_use import Agent
    from config import (
        SEARCH_KEYWORDS, SEARCH_LOCATION, DAILY_LIMITS,
        DELAY_MIN_SECONDS, DELAY_MAX_SECONDS,
        JOB_POSTED_WITHIN, HUMAN_APPROVAL_MODE,
    )
    from profile import PROFILE

    limit = DAILY_LIMITS.get(platform, 20)

    task = build_compact_prompt(
        profile       = PROFILE,
        platform      = platform,
        limit         = limit,
        search_kw     = SEARCH_KEYWORDS,
        location      = SEARCH_LOCATION,
        delay_min     = DELAY_MIN_SECONDS,
        delay_max     = DELAY_MAX_SECONDS,
        posted_within = JOB_POSTED_WITHIN,
        approval_mode = HUMAN_APPROVAL_MODE,
        mode_instructions = mode_instructions,
    )

    agent = Agent(
        task                  = task,
        llm                   = get_llm(),
        browser               = browser,
        flash_mode            = True,
        save_conversation_path= "logs/screenshots/",
    )

    return await agent.run(max_steps=max(25, limit * 3))