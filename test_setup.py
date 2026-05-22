# test_setup.py
import asyncio
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

async def test_api_key():
    """
    Test whichever LLM provider is set in config.py.
    Works for Claude, OpenAI, Gemini, OpenRouter, and AgentRouter.
    """
    print("Testing API key...", end=" ")
    try:
        from config import LLM_PROVIDER, LLM_MODELS
        if LLM_PROVIDER == "claude":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model=LLM_MODELS["claude"])
        elif LLM_PROVIDER == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=LLM_MODELS["openai"])
        elif LLM_PROVIDER == "gemini":
            from browser_use.llm.google.chat import ChatGoogle
            llm = ChatGoogle(model=LLM_MODELS["gemini"])
        elif LLM_PROVIDER == "openrouter":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                print("✗ FAILED: OPENROUTER_API_KEY is not set in .env")
                return
            llm = ChatOpenAI(
                model=LLM_MODELS["openrouter"],
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        elif LLM_PROVIDER == "agentrouter":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("AGENTROUTER_API_KEY")
            if not api_key:
                print("✗ FAILED: AGENTROUTER_API_KEY is not set in .env")
                return
            llm = ChatOpenAI(
                model=LLM_MODELS["agentrouter"],
                base_url="https://agentrouter.org/v1",
                api_key=api_key,
            )
        else:
            print(f"✗ FAILED: Unknown LLM_PROVIDER '{LLM_PROVIDER}' in config.py")
            print(f"  Valid options: 'claude', 'openai', 'gemini', 'openrouter', 'agentrouter'")
            return
        response = llm.invoke("Say 'API key works' and nothing else.")
        print(f"✓ OK [{LLM_PROVIDER}]:", response.content.strip())
    except Exception as e:
        print("✗ FAILED:", e)

async def test_browser():
    """Test that the browser launches and can load a page."""
    print("Testing browser...", end=" ")
    try:
        # browser-use installs playwright as a dependency, so we can use it directly
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page    = await browser.new_page()
            await page.goto("https://example.com")
            title   = await page.title()
            await browser.close()
        print(f"✓ OK (loaded: {title})")
    except Exception as e:
        print("✗ FAILED:", e)

async def test_chrome_profile():
    """Test that Browser.from_system_chrome() can connect to your Chrome profile."""
    print("Testing Chrome profile...", end=" ")
    profile = os.getenv("CHROME_PROFILE")
    if not profile:
        print("⚠ SKIPPED (CHROME_PROFILE not set in .env)")
        return
    try:
        from browser_use import BrowserSession
        browser = BrowserSession.from_system_chrome(profile_directory=profile)
        await browser.stop()
        print(f"✓ OK (profile: {profile})")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print("  → Make sure Chrome is fully closed before running this test.")

def test_profile_file():
    """Test that profile.py is correctly filled in."""
    print("Testing profile.py...", end=" ")
    try:
        from profile import PROFILE
        required = ["name", "email", "phone", "resume_path", "primary_skills"]
        missing = [k for k in required if not PROFILE.get(k)]
        if missing:
            print(f"✗ Missing fields: {missing}")
        elif not os.path.exists(PROFILE["resume_path"]):
            print(f"✗ Resume not found at: {PROFILE['resume_path']}")
        else:
            print(f"✓ OK (profile for: {PROFILE['name']})")
    except Exception as e:
        print("✗ FAILED:", e)

def test_tracker():
    """Test that the SQLite tracker initialises correctly."""
    print("Testing tracker...", end=" ")
    try:
        from tracker import init_db
        conn = init_db()
        conn.close()
        print("✓ OK")
    except Exception as e:
        print("✗ FAILED:", e)

async def main():
    print("\n" + "="*50)
    print("  Browser-Use Setup Test")
    print("="*50 + "\n")

    test_profile_file()
    test_tracker()
    await test_api_key()
    await test_browser()
    await test_chrome_profile()

    print("\n" + "="*50)
    print("  Tests complete. Fix any ✗ errors before running main.py.")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())