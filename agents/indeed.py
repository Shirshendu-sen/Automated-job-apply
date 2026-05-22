# agents/indeed.py

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


def build_indeed_prompt(
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
Apply ONLY if highly relevant.

- Click:
  Apply Now
  Easily Apply

- Skip:
  Apply on company site

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

Notice Period:
{profile['notice_period']}

Upload resume:
{profile['resume_path']}

If screening questions appear:
Answer professionally using candidate profile.

If cover letter needed:
Use:
{profile['cover_letter_summary']}

After successful apply print EXACTLY:

APPLIED: [job title] at [company]

If skipped print:

SKIPPED: [job title] — [reason]
"""
    )

    return f"""
You are an intelligent AI assistant helping
{profile['name']}
apply for highly relevant software engineering jobs on Indeed India.

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
STEP 1 — NAVIGATE
────────────────────────────────────────

Go to:
https://in.indeed.com

────────────────────────────────────────
STEP 2 — SEARCH
────────────────────────────────────────

In "What" field enter:
{SEARCH_KEYWORDS}

In "Where" field enter:
{SEARCH_LOCATION}

Click:
Find Jobs

────────────────────────────────────────
STEP 3 — APPLY FILTERS
────────────────────────────────────────

Apply these filters if available:

- Experience:
  {profile['experience_years']} years

- Salary:
  Minimum {profile['min_salary_lpa']} LPA

- Work mode:
  Remote / Hybrid preferred

- Date Posted:
  {freshness_filter}

────────────────────────────────────────
STEP 4 — REVIEW JOBS
────────────────────────────────────────

For each job:

A. Read:
- Job title
- Company
- Skills
- Experience required
- Job summary

B. SKIP if:
- Already applied
- "Apply on company site"
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
- Startup/product companies
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


async def apply_indeed(
    browser: BrowserSession,
    mode_instructions: str = ""
):

    limit = DAILY_LIMITS.get("indeed", 15)

    agent = Agent(
        task=build_indeed_prompt(
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