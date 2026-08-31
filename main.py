"""Entry point for the FCAP platform.

Run with: python main.py
"""

import uvicorn

from fcap import config
from fcap.llm import get_gpt_oss_response


def main() -> None:
    print("🏥 Starting Robust GPT-OSS-20B FCAP Platform...")
    print(f"🌐 Patient Interface: http://localhost:{config.PORT}")
    print(f"🏥 Clinic Interface: http://localhost:{config.PORT}/clinic")
    print(f"🔧 Admin Interface: http://localhost:{config.PORT}/admin")
    print("🤖 AI Assistant: GPT-OSS-20B ONLY - No Fallbacks")
    print(f"🔍 Health Check: http://localhost:{config.PORT}/health/llm")
    print("=" * 60)

    # Test GPT-OSS-20B connection on startup
    try:
        test_response = get_gpt_oss_response("Hello")
        print(f"✅ GPT-OSS-20B Connection Test: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ GPT-OSS-20B Connection Test Failed: {e}")
        print("   Platform will start but AI may not work properly")

    uvicorn.run("fcap.api:app", host=config.HOST, port=config.PORT, reload=True)


if __name__ == "__main__":
    main()
