#!/usr/bin/env python3
"""Static validation script for job-bot. Runs all 6 checks."""
import sys, os, traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

PASS = []
WARN = []
FAIL = []

def check(name, condition, msg, warn_only=False):
    if condition:
        PASS.append("[PASS] %s: %s" % (name, msg))
        print("  [PASS] %s: %s" % (name, msg))
    elif warn_only:
        WARN.append("[WARN] %s: %s" % (name, msg))
        print("  [WARN] %s: %s" % (name, msg))
    else:
        FAIL.append("[FAIL] %s: %s" % (name, msg))
        print("  [FAIL] %s: %s" % (name, msg))


###############################################################################
# CHECK 1 -- IMPORTS
###############################################################################
print("=" * 60)
print("CHECK 1 -- IMPORTS")
print("=" * 60)

# 1a. Test agents/*.py can be parsed by importing base.py exports from them
#     (Full import of agent files requires browser_use which is in uv env)
#     We test base.py which is the actual "source of truth" and which main.py uses.
import agents.base as base
for fn_name in ["get_llm", "build_compact_prompt", "run_agent"]:
    cond = hasattr(base, fn_name) and callable(getattr(base, fn_name))
    check("agents.base exports %s()" % fn_name, cond,
          "exists and callable" if cond else "NOT FOUND or not callable")

# 1b. Confirm each agent file exists and is non-empty
for mod_name in ["naukri", "linkedin", "indeed", "instahyre"]:
    path = "agents/%s.py" % mod_name
    if os.path.exists(path):
        lines = open(path, "r", encoding="utf-8").readlines()
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        if len(code_lines) <= 3:
            check("agents/%s.py content" % mod_name, False,
                  "Only %d code lines -- consider deleting" % len(code_lines))
        else:
            check("agents/%s.py exists + non-empty" % mod_name, True,
                  "%d code lines" % len(code_lines))
    else:
        check("agents/%s.py exists" % mod_name, False, "File not found: %s" % path)

# 1c. Test agents can be imported via uv run (they need browser_use)
#     We mark this as WARN since system Python may not have browser_use installed,
#     but the project uses 'uv run' to manage environments.
try:
    import agents.naukri
    check("agents.naukri import", True, "imported OK")
except ImportError as e:
    check("agents.naukri import", False, "ImportError: %s" % str(e)[:80], warn_only=True)

try:
    import agents.linkedin
    check("agents.linkedin import", True, "imported OK")
except ImportError as e:
    check("agents.linkedin import", False, "ImportError: %s" % str(e)[:80], warn_only=True)

try:
    import agents.indeed
    check("agents.indeed import", True, "imported OK")
except ImportError as e:
    check("agents.indeed import", False, "ImportError: %s" % str(e)[:80], warn_only=True)

try:
    import agents.instahyre
    check("agents.instahyre import", True, "imported OK")
except ImportError as e:
    check("agents.instahyre import", False, "ImportError: %s" % str(e)[:80], warn_only=True)

# 1d. modes/*.py imports
for mod_name, var_name in [
    ("safe", "SAFE_MODE_INSTRUCTIONS"),
    ("aggressive", "AGGRESSIVE_MODE_INSTRUCTIONS"),
    ("startup", "STARTUP_MODE_INSTRUCTIONS"),
    ("fresher", "FRESHER_MODE_INSTRUCTIONS"),
    ("remote", "REMOTE_MODE_INSTRUCTIONS"),
]:
    try:
        mod = __import__("modes.%s" % mod_name, fromlist=[var_name])
        val = getattr(mod, var_name, None)
        cond = val is not None and isinstance(val, str) and len(val.strip()) > 0
        check("modes.%s.%s" % (mod_name, var_name), cond,
              "non-empty string" if cond else "missing or empty")
    except Exception as e:
        check("modes.%s.%s" % (mod_name, var_name), False, str(e))

# 1e. modes/__init__.py exists
check("modes/__init__.py exists", os.path.exists("modes/__init__.py"), "exists")


###############################################################################
# CHECK 2 -- ENV & CONFIG
###############################################################################
print("\n" + "=" * 60)
print("CHECK 2 -- ENV & CONFIG")
print("=" * 60)

from dotenv import load_dotenv
load_dotenv()

# 2a. At least one API key
api_keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "AGENTROUTER_API_KEY"]
found = False
for k in api_keys:
    v = os.getenv(k, "")
    if v and len(v) > 10:
        found = True
        break
check("At least one API key in .env", found,
      "at least one key set" if found else "NO valid API key found")

# 2b. LLM_PROVIDER matches a key in LLM_MODELS
from config import LLM_PROVIDER, LLM_MODELS
check("LLM_PROVIDER in LLM_MODELS", LLM_PROVIDER in LLM_MODELS,
      "'%s' -> '%s'" % (LLM_PROVIDER, LLM_MODELS.get(LLM_PROVIDER, "MISSING")))

# 2c. DAILY_LIMITS total <= 100
from config import DAILY_LIMITS
total = sum(DAILY_LIMITS.values())
check("DAILY_LIMITS total <= 100", total <= 100,
      "total=%d" % total, warn_only=(total > 100))

# 2d. DELAY_MIN_SECONDS >= 5
from config import DELAY_MIN_SECONDS
if DELAY_MIN_SECONDS < 5:
    check("DELAY_MIN_SECONDS >= 5", False,
          "got %d -- REQUIRES FIX (set to 5)" % DELAY_MIN_SECONDS)
else:
    check("DELAY_MIN_SECONDS >= 5", True, "value=%d" % DELAY_MIN_SECONDS)

# 2e. PLATFORM_GAP_MIN >= 60
from config import PLATFORM_GAP_MIN
check("PLATFORM_GAP_MIN >= 60", PLATFORM_GAP_MIN >= 60,
      "value=%d" % PLATFORM_GAP_MIN, warn_only=(PLATFORM_GAP_MIN < 60))

# 2f. HUMAN_APPROVAL_MODE is bool
from config import HUMAN_APPROVAL_MODE
check("HUMAN_APPROVAL_MODE is bool", isinstance(HUMAN_APPROVAL_MODE, bool),
      "type=%s value=%s" % (type(HUMAN_APPROVAL_MODE).__name__, HUMAN_APPROVAL_MODE))


###############################################################################
# CHECK 3 -- PROFILE
###############################################################################
print("\n" + "=" * 60)
print("CHECK 3 -- PROFILE")
print("=" * 60)

from profile import PROFILE

required = ["name", "email", "phone", "primary_skills", "experience_years",
            "expected_ctc", "notice_period", "min_salary_lpa", "resume_path",
            "cover_letter_summary", "blacklisted_companies"]
for k in required:
    cond = k in PROFILE
    check("PROFILE['%s'] exists" % k, cond,
          "value=%s" % repr(PROFILE.get(k, "MISSING")) if cond else "MISSING KEY")

# 3b. resume_path exists on disk
rp = PROFILE.get("resume_path", "")
if rp and os.path.exists(rp):
    check("resume_path exists", True, "%s" % rp)
elif rp:
    check("resume_path exists", False,
          "NOT FOUND: %s -- Copy your resume to: %s" % (rp, rp))
else:
    check("resume_path", False, "resume_path is empty -- set it in profile.py")

# 3c. primary_skills is non-empty list
ps = PROFILE.get("primary_skills", [])
check("primary_skills non-empty list", isinstance(ps, list) and len(ps) > 0,
      "%d skills" % len(ps))

# 3d. cover_letter_summary is non-empty string
cls = PROFILE.get("cover_letter_summary", "")
check("cover_letter_summary non-empty", isinstance(cls, str) and len(cls.strip()) > 0,
      "length=%d" % len(cls))


###############################################################################
# CHECK 4 -- TRACKER
###############################################################################
print("\n" + "=" * 60)
print("CHECK 4 -- TRACKER")
print("=" * 60)

import tracker

for fn_name in ["log_application", "already_applied", "daily_report"]:
    cond = hasattr(tracker, fn_name) and callable(getattr(tracker, fn_name))
    check("tracker.%s()" % fn_name, cond,
          "exists and callable" if cond else "MISSING")

# 4b. Create logs/ and logs/screenshots/
for d in ["logs", "logs/screenshots"]:
    os.makedirs(d, exist_ok=True)
    check("Directory %s/" % d, os.path.isdir(d),
          "exists" if os.path.isdir(d) else "CREATED")

# 4c. Test DB schema creation
try:
    conn = tracker.init_db()
    check("tracker.init_db()", True, "schema created without crash")
except Exception as e:
    conn = None
    check("tracker.init_db()", False, str(e))

# 4d. Test insert + query + delete one dummy row
if conn:
    try:
        tracker.log_application(conn, "TEST_JOB", "TEST_CO", "naukri",
                                "applied", reason="test",
                                job_url="http://example.com/test123")
        cur = conn.execute(
            "SELECT * FROM applications WHERE job_url='http://example.com/test123'")
        row = cur.fetchone()
        check("DB insert + query", row is not None,
              "row found" if row else "row NOT found")

        # Test already_applied
        aa = tracker.already_applied(conn, "http://example.com/test123")
        check("already_applied() TRUE", aa is True, "returned %s" % aa)

        aa2 = tracker.already_applied(conn, "http://example.com/nonexistent")
        check("already_applied() FALSE for new URL", aa2 is False,
              "returned %s" % aa2)

        # Test daily_report
        dr = tracker.daily_report(conn)
        check("daily_report() returns list", isinstance(dr, list),
              "got %d rows" % len(dr))

        # Delete dummy
        conn.execute(
            "DELETE FROM applications WHERE job_url='http://example.com/test123'")
        conn.commit()
        cur2 = conn.execute(
            "SELECT * FROM applications WHERE job_url='http://example.com/test123'")
        check("DB delete", cur2.fetchone() is None, "dummy row cleaned up")

    except Exception as e:
        check("DB write test", False, str(e))
        traceback.print_exc()
    finally:
        conn.close()


###############################################################################
# CHECK 5 -- BUILD_COMPACT_PROMPT
###############################################################################
print("\n" + "=" * 60)
print("CHECK 5 -- BUILD_COMPACT_PROMPT")
print("=" * 60)

from agents.base import build_compact_prompt
from config import SEARCH_KEYWORDS, SEARCH_LOCATION, DELAY_MIN_SECONDS as D_MIN
from config import DELAY_MAX_SECONDS as D_MAX, JOB_POSTED_WITHIN

for plat in ["naukri", "linkedin", "indeed", "instahyre"]:
    try:
        out = build_compact_prompt(
            profile=PROFILE,
            platform=plat,
            limit=20,
            search_kw=SEARCH_KEYWORDS,
            location=SEARCH_LOCATION,
            delay_min=D_MIN,
            delay_max=D_MAX,
            posted_within=JOB_POSTED_WITHIN,
            approval_mode=True,
            mode_instructions="TEST MODE",
        )
        cond_str = isinstance(out, str) and len(out) > 0
        has_url = "GO TO: https://" in out
        check("build_compact_prompt(%s)" % plat, cond_str and has_url,
              "len=%d, GO_TO_URL=%s" % (len(out), "YES" if has_url else "NO"))
    except Exception as e:
        check("build_compact_prompt(%s)" % plat, False, str(e))

# 5c. Unknown platform should NOT return empty URL silently
try:
    out = build_compact_prompt(PROFILE, "unknown", 20, SEARCH_KEYWORDS,
                               SEARCH_LOCATION, 10, 30, "7d", True, "")
    # The current implementation returns empty string for URL but does NOT raise.
    # Check: does the output have "GO TO: " with empty URL?
    if "GO TO: " not in out:
        check("Unknown platform raises error", False,
              "NO error raised, and no GO TO: in output (silent failure)")
    else:
        # It may have GO TO: with empty URL
        check("Unknown platform raises error", False,
              "No error raised, GO TO present but URL may be empty -- should raise ValueError")
except ValueError:
    check("Unknown platform raises error", True,
          "ValueError raised as expected")
except Exception as e:
    check("Unknown platform raises error", False,
          "Wrong error type: %s: %s" % (type(e).__name__, e))


###############################################################################
# CHECK 6 -- GET_LLM
###############################################################################
print("\n" + "=" * 60)
print("CHECK 6 -- GET_LLM")
print("=" * 60)

from agents.base import get_llm
try:
    llm = get_llm()
    obj_type = type(llm).__name__
    check("get_llm() initializes", True, "returned %s object" % obj_type)
except ValueError as e:
    msg = str(e)
    check("get_llm() initializes", False, "ValueError: %s" % msg)
except Exception as e:
    check("get_llm() initializes", False, "%s: %s" % (type(e).__name__, e))


###############################################################################
# REPORT
###############################################################################
print("\n" + "=" * 60)
print("STATIC CHECK REPORT")
print("=" * 60)
print("PASS: %d  WARN: %d  FAIL: %d" % (len(PASS), len(WARN), len(FAIL)))
print()
for item in PASS + WARN + FAIL:
    print(item)

sys.exit(1 if FAIL else 0)