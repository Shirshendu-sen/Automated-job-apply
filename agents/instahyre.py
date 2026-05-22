# agents/instahyre.py

# ── NOTE ─────────────────────────────────────────────────────────────────────
# Instahyre focuses heavily on:
# - product companies
# - startups
# - software engineering roles
#
# Response quality is usually better than mass-job portals.
# ─────────────────────────────────────────────────────────────────────────────

from browser_use import Agent, BrowserSession
from agents.base import get_llm
from profile import PROFILE

from config import (
    SEARCH_KEYWORDS,
    SEARCH_LOCATION,
    DAILY_LIMITS,
    DELAY_MIN_SECONDS,
    DELAY_MAX_SECONDS,
    JOB_POSTED_WITHIN,
    HUMAN_APPROVAL_MODE,
)


def build_instahyre_prompt(
    profile: dict,
    limit: int,
    mode_instructions: str = ""
) -> str:

    skills_str = ", ".join(profile["primary_skills"])
    blacklist = ", ".join(profile["blacklisted_companies"])

    freshness_filter = (
        "Last 24 hours"
        if JOB_POSTED_WITHIN == "24h"
        else "Last 3 days"
        if JOB_POSTED_WITHIN == "3d"
        else "Last 7 days"
        if JOB_POSTED_WITHIN == "7d"
        else "Last 30 days"
        if JOB_POSTED_WITHIN == "30d"
        else "Any time"
    )

    approval_section = (
        """
IMPORTANT:
DO NOT APPLY DIRECTLY.

Instead:

1. Open the job.
2. Extract:
   - Job title
   - Company
   - Job URL
   - Required skills
   - Salary if available
   - Why it matches candidate profile

3. Print EXACTLY:

SHORTLISTED: [job title] at [company]
URL: [job URL]

4. Continue to next job.
"""
        if HUMAN_APPROVAL_MODE
        else f"""
Apply ONLY if the role is highly relevant.

- Click:
  Apply
  Express Interest

- Fill forms carefully.

Use:

Name:
{profile['name']}

Email:
{profile['email']}

Phone:
{profile['phone']}

Experience:
{profile['experience_years']} years

Current CTC:
{profile['current_ctc']}

Expected CTC:
{profile['expected_ctc']}

Upload resume:
{profile['resume_path']}

If additional questions appear:
Answer professionally using candidate profile.

After successful apply print EXACTLY:

APPLIED: [job title] at [company]

If skipped print:

SKIPPED: [job title] — [reason]
"""
    )

    return f"""
You are an intelligent AI assistant helping
{profile['name']}
apply for highly relevant software engineering jobs on Instahyre.

{mode_instructions}

IMPORTANT RULES:
- Focus ONLY on:
  Backend Developer
  Full Stack Developer
  Software Engineer
  Python Developer
  Node.js Developer
  React Developer
  Next.js Developer
  AI Engineer
  Generative AI Engineer

- Prefer:
  Product companies
  Startups
  Remote jobs
  Hybrid jobs

- Prefer technologies:
  Python
  Node.js
  React
  Next.js
  REST APIs
  Microservices
  AI/ML
  Cloud
  CI/CD

- Skip:
  BPO
  Support
  Non-tech
  Sales
  Analyst
  Testing-only jobs

────────────────────────────────────────
STEP 1 — GO TO INSTAHYRE
────────────────────────────────────────

Navigate to:
https://www.instahyre.com

If login screen appears:
- use existing Chrome session
- do NOT create a new account

────────────────────────────────────────
STEP 2 — SEARCH
────────────────────────────────────────

Use search bar and search for:
{SEARCH_KEYWORDS}

If location filter is available, set to:
{SEARCH_LOCATION}

────────────────────────────────────────
STEP 3 — APPLY FILTERS
────────────────────────────────────────

Apply these filters if available:

- Experience:
  {profile['experience_years']} years

- Date Posted:
  {freshness_filter}

- Work mode:
  Remote / Hybrid preferred

────────────────────────────────────────
STEP 4 — REVIEW JOBS
────────────────────────────────────────

For each matching job:

A. Read:
- Job title
- Company
- Skills
- Experience required
- Job summary

B. SKIP if:
- Already applied
- Experience required is more than
  {profile['experience_years'] + 2} years
- No overlap with:
  {skills_str}
- Company contains:
  {blacklist}
- Job is unrelated to software development

C. Prefer:
- Backend roles
- Full-stack roles
- AI/ML projects
- Product companies
- Startup environments
- Remote/hybrid jobs

────────────────────────────────────────
STEP 5 — APPLICATION FLOW
────────────────────────────────────────

{approval_section}

────────────────────────────────────────
STEP 6 — DELAYS
────────────────────────────────────────

Wait random time between
{DELAY_MIN_SECONDS}
and
{DELAY_MAX_SECONDS}
seconds between jobs.

────────────────────────────────────────
STEP 7 — STOP
────────────────────────────────────────

Stop after:
- {limit} jobs
OR
- 5 pages

At end print summary:

Total shortlisted: X / Total applied: Y / Total skipped: Z
"""


async def apply_instahyre(
    browser: BrowserSession,
    mode_instructions: str = ""
):

    limit = DAILY_LIMITS.get("instahyre", 10)

    agent = Agent(
        task=build_instahyre_prompt(
            PROFILE,
            limit,
            mode_instructions
        ),
        llm=get_llm(),
        browser=browser,
        flash_mode=True,

        # Saves screenshots/conversation history
        save_conversation_path="logs/screenshots/",
    )

    return await agent.run(max_steps=max(25, limit * 3))