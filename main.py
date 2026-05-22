# main.py
import asyncio
import random
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from browser_use import BrowserSession, BrowserProfile

sys.stdout.reconfigure(encoding="utf-8")

from config import (
    ACTIVE_PLATFORMS, DELAY_MIN_SECONDS, DELAY_MAX_SECONDS,
    HEADLESS, PLATFORM_GAP_MIN, PLATFORM_GAP_MAX
)
from tracker import init_db, daily_report, log_application
from agents.base import run_agent

load_dotenv()

# ── Logging setup ─────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/run_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(),   # also print to terminal
    ]
)
logger = logging.getLogger(__name__)

# ── Helper: load mode instructions ────────────────────────────────────────────
def get_mode_instructions() -> str:
    """
    Reads RUN_MODE from config.py and returns the matching instruction text.
    This text is injected at the top of every agent's prompt so the AI knows
    which filtering strategy to use.
    """
    from config import RUN_MODE
    if RUN_MODE == "safe":
        from modes.safe import SAFE_MODE_INSTRUCTIONS
        return SAFE_MODE_INSTRUCTIONS
    elif RUN_MODE == "aggressive":
        from modes.aggressive import AGGRESSIVE_MODE_INSTRUCTIONS
        return AGGRESSIVE_MODE_INSTRUCTIONS
    elif RUN_MODE == "startup":
        from modes.startup import STARTUP_MODE_INSTRUCTIONS
        return STARTUP_MODE_INSTRUCTIONS
    elif RUN_MODE == "fresher":
        from modes.fresher import FRESHER_MODE_INSTRUCTIONS
        return FRESHER_MODE_INSTRUCTIONS
    elif RUN_MODE == "remote":
        from modes.remote import REMOTE_MODE_INSTRUCTIONS
        return REMOTE_MODE_INSTRUCTIONS
    return ""   # No special mode — use default agent behaviour

# ── Helper: create browser using system Chrome ────────────────────────────────
def create_browser() -> BrowserSession:
    """
    Connects to your real installed Chrome via BrowserSession.from_system_chrome().
    Supports persistent user_data_dir for session cookie reuse (bypass logins).
    Set CHROME_PROFILE in .env (e.g. "Default" or "Profile 1").
    Set CHROME_USER_DATA_DIR in .env to override default Chrome profile path.
    Falls back to managed Chromium if Chrome is unavailable.
    """
    profile = os.getenv("CHROME_PROFILE", "Default")
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR", None)
    try:
        return BrowserSession.from_system_chrome(
            profile_directory=profile,
            user_data_dir=user_data_dir,
        )
    except Exception as e:
        print(f"WARNING: Could not connect to system Chrome ({e}).")
        print("         Falling back to managed Chromium — log in manually.")
        return BrowserSession(
            browser_profile=BrowserProfile(
                headless=HEADLESS,
                user_data_dir=user_data_dir,
                profile_directory=profile,
            )
        )

# ── Helper: parse agent output and log each line to tracker DB ────────────────
def parse_and_log(conn, result, platform: str):
    """
    Agents print 'APPLIED: title at company' or 'SKIPPED: title — reason'.
    This function reads those lines and writes them to the SQLite tracker.
    """
    if result is None:
        return
    output = str(result)
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("APPLIED:"):
            parts = line[len("APPLIED:"):].split(" at ", 1)
            title   = parts[0].strip() if parts else line
            company = parts[1].strip() if len(parts) > 1 else "Unknown"
            log_application(conn, title, company, platform, "applied")
        elif line.startswith("SKIPPED:"):
            parts = line[len("SKIPPED:"):].split("—", 1)
            title  = parts[0].strip() if parts else line
            reason = parts[1].strip() if len(parts) > 1 else ""
            log_application(conn, title, "", platform, "skipped", reason=reason)

# ── Main runner ───────────────────────────────────────────────────────────────
async def daily_run():
    conn              = init_db()
    browser           = create_browser()
    mode_instructions = get_mode_instructions()

    print(f"\n{'='*60}")
    print(f"  Job Bot — Daily Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    for i, platform in enumerate(ACTIVE_PLATFORMS):
        print(f"\n{'─'*60}")
        print(f"  Starting: {platform.upper()}")
        print(f"{'─'*60}")
        try:
            result = await run_agent(platform, browser, mode_instructions)
            parse_and_log(conn, result, platform)
            print(f"  ✓ {platform} done")
        except Exception as e:
            print(f"  ✗ {platform} failed: {e}")
            log_application(conn, "N/A", "N/A", platform, "failed", reason=str(e))

        # Do not sleep after the last platform
        if i < len(ACTIVE_PLATFORMS) - 1:
            gap = random.randint(PLATFORM_GAP_MIN, PLATFORM_GAP_MAX)
            print(f"\n  Waiting {gap // 60} min {gap % 60} sec before next platform...\n")
            await asyncio.sleep(gap)

    # Print today's summary
    report = daily_report(conn)
    print("\n📊 Today's Summary")
    print("─" * 40)
    for row in report:
        print(f"  {row[0]:15} {row[1]:10} {row[2]} jobs")

    await browser.stop()
    conn.close()

if __name__ == "__main__":
    asyncio.run(daily_run())
