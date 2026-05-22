# agents/naukri.py

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

def build_naukri_prompt(
    profile: dict,
    limit: int,
    mode_instructions: str = ""
) -> str:

    skills_str = ", ".join(profile["primary_skills"])
    blacklist  = ", ".join(profile["blacklisted_companies"])

    return f"""
You are an intelligent AI job assistant helping {profile['name']}
apply for highly relevant software engineering jobs on Naukri.com.

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

- Prefer product-based companies and startups.
- Prefer jobs involving:
  Python
  Node.js
  React
  Next.js
  REST APIs
  Microservices
  AI/ML
  Cloud
  CI/CD
  Backend systems

- Skip support, BPO, testing-only, analyst, sales, or non-development jobs.
- Skip mass recruiters if possible.
- Prefer recent jobs only.

────────────────────────────────────────
STEP 1 — SEARCH
────────────────────────────────────────

Go to:
https://www.naukri.com

In the search field enter:
{SEARCH_KEYWORDS}

Set location to:
{SEARCH_LOCATION}

Click Search.

If login popup appears:
- close it
- press Escape if needed

────────────────────────────────────────
STEP 2 — APPLY FILTERS
────────────────────────────────────────

Apply these filters if available:

- Experience:
  {profile['experience_years']} years

- Salary:
  Minimum {profile['min_salary_lpa']} LPA

- Work mode:
  Remote / Hybrid preferred

- Freshness filter:
"""
    + (
        """
- Last 1 day
"""
        if JOB_POSTED_WITHIN == "24h"
        else """
- Last 3 days
"""
        if JOB_POSTED_WITHIN == "3d"
        else """
- Last 7 days
"""
        if JOB_POSTED_WITHIN == "7d"
        else """
- Last 30 days
"""
        if JOB_POSTED_WITHIN == "30d"
        else """
- Any time
"""
    ) + f"""

────────────────────────────────────────
STEP 3 — REVIEW JOBS
────────────────────────────────────────

For each job listing:

A. Read:
- Job title
- Company name
- Skills
- Experience required
- First part of description

B. SKIP the job if:
- Already applied
- Experience required is more than {profile['experience_years'] + 2} years
- No overlap with these skills:
  {skills_str}
- Company contains:
  {blacklist}
- Job is unrelated to software development
- Job is support/BPO/call-center/testing-only

C. Prefer:
- AI/ML projects
- Backend engineering
- Full-stack development
- Cloud engineering
- Startup/product companies
- Remote/hybrid jobs

────────────────────────────────────────
STEP 4 — HUMAN APPROVAL MODE
────────────────────────────────────────
"""
    + (
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

4. Move to next job.

"""
        if HUMAN_APPROVAL_MODE
        else f"""
Apply automatically ONLY if the job is highly relevant.

- Click Apply / Apply Now / Easy Apply
- Fill forms carefully
- Upload resume:
  {profile['resume_path']}

Use these details:

Name: {profile['name']}
Email: {profile['email']}
Phone: {profile['phone']}
Experience: {profile['experience_years']} years
Current CTC: {profile['current_ctc']}
Expected CTC: {profile['expected_ctc']}
Notice Period: {profile['notice_period']}

If cover letter required:
Use:
{profile['cover_letter_summary']}

After successful apply print EXACTLY:

APPLIED: [job title] at [company]

If skipped print:

SKIPPED: [job title] — [reason]
"""
    ) + f"""

────────────────────────────────────────
STEP 5 — DELAYS
────────────────────────────────────────

Wait random time between
{DELAY_MIN_SECONDS}
and
{DELAY_MAX_SECONDS}
seconds between jobs.

────────────────────────────────────────
STEP 6 — STOP
────────────────────────────────────────

Stop after:
- {limit} jobs
OR
- 5 pages

At end print summary:

Total shortlisted: X / Total applied: Y / Total skipped: Z
"""


async def apply_naukri(
    browser: BrowserSession,
    mode_instructions: str = ""
):

    limit = DAILY_LIMITS.get("naukri", 20)

    agent = Agent(
        task=build_naukri_prompt(
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