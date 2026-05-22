# agents/linkedin.py
# ── IMPORTANT NOTE ABOUT LINKEDIN ────────────────────────────────────────────
# LinkedIn is very aggressive about bot detection.
# You MUST use your existing logged-in Chrome profile (see Section 10).
# Only target "Easy Apply" jobs — external applications open a new website
# and are much harder to automate reliably.
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

def build_linkedin_prompt(profile: dict, limit: int, mode_instructions: str = "") -> str:
    skills_str = ", ".join(profile["primary_skills"])
    blacklist = ", ".join(profile["blacklisted_companies"])

    return f"""
You are helping {profile['name']} apply for jobs on LinkedIn.

{mode_instructions}

IMPORTANT: Only apply to jobs with the "Easy Apply" button.
If a job shows an "Apply" button that takes you to an external website, skip it.

────────────────────────────────────────
STEP 1 — NAVIGATE
────────────────────────────────────────

Go to: https://www.linkedin.com/jobs/search/
You should already be logged in. If not, stop and report "Not logged in to LinkedIn".

────────────────────────────────────────
STEP 2 — SEARCH
────────────────────────────────────────

In the job search field, type: {SEARCH_KEYWORDS}
In the location field, type: {SEARCH_LOCATION}
Click the Search button.

────────────────────────────────────────
STEP 3 — APPLY FILTERS
────────────────────────────────────────

After search results load:
- Click "All Filters" or look for "Easy Apply" toggle and turn it ON.
"""
    + (
        """
- Set "Date posted" to "Past 24 hours".
"""
        if JOB_POSTED_WITHIN == "24h"
        else """
- Set "Date posted" to "Past week".
"""
        if JOB_POSTED_WITHIN in ("3d", "7d")
        else """
- Set "Date posted" to "Past month".
"""
        if JOB_POSTED_WITHIN == "30d"
        else """
- Skip date posted filter (show all results).
"""
    ) + f"""
- Set "Experience level" to "Mid-Senior level" or "Associate".

────────────────────────────────────────
STEP 4 — REVIEW JOBS
────────────────────────────────────────

For each job listing:

A. Read:
- Job title
- Company name
- Skills required
- Experience required
- First part of description

B. SKIP the job if:
- Already applied
- Not "Easy Apply"
- Experience required is more than {profile['experience_years'] + 2} years
- No overlap with these skills:
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

4. Continue to next job.

"""
        if HUMAN_APPROVAL_MODE
        else f"""
Apply ONLY if the role is highly relevant.

a. Click the job to open the detail panel on the right.
b. Click "Easy Apply".
c. A multi-step form will appear. Follow each step:
   - Contact info: confirm name={profile['name']}, email={profile['email']}, phone={profile['phone']}
   - Resume: upload {profile['resume_path']} if prompted
   - Questions: answer honestly based on profile details
     - Years of experience: {profile['experience_years']}
     - Authorised to work in India: Yes
     - Require sponsorship: No
     - Willing to relocate: Yes
   - Cover letter (if asked): {profile['cover_letter_summary']}
d. Click "Submit application" on the final step.
e. Print: APPLIED: [title] at [company]

If skipped print:

SKIPPED: [job title] — [reason]
"""
    ) + f"""

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
- 3 pages of results

At end print summary:

Total shortlisted: X / Total applied: Y / Total skipped: Z
"""


async def apply_linkedin(browser: BrowserSession, mode_instructions: str = ""):
    limit = DAILY_LIMITS.get("linkedin", 10)

    agent = Agent(
        task=build_linkedin_prompt(PROFILE, limit, mode_instructions),
        llm=get_llm(),
        browser=browser,
        flash_mode=True,

        # Saves screenshots/conversation history
        save_conversation_path="logs/screenshots/",
    )

    return await agent.run(max_steps=max(25, limit * 3))