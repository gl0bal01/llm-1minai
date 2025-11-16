#!/usr/bin/env python3
"""
Simple script to test if web_search is actually being sent to the API.
This intercepts the API call and shows what's being sent.
"""

import json
import sys
from unittest.mock import patch

import llm


def test_web_search_enabled():
    """Test that web_search from config is included in the request."""

    # Track if web_search was sent
    web_search_sent = False
    original_post = None

    def mock_post(url, **kwargs):
        nonlocal web_search_sent, original_post

        if "features" in url:
            payload = kwargs.get("json", {})
            prompt_obj = payload.get("promptObject", {})

            print("\n" + "=" * 70)
            print("API REQUEST TO:", url)
            print("=" * 70)
            print("Full payload:")
            print(json.dumps(payload, indent=2))
            print("=" * 70)

            if "webSearch" in prompt_obj:
                web_search_sent = True
                print("✅ webSearch IS included in the request!")
                print(f"   webSearch: {prompt_obj['webSearch']}")
                print(f"   numOfSite: {prompt_obj.get('numOfSite', 'not set')}")
                print(f"   maxWord: {prompt_obj.get('maxWord', 'not set')}")
            else:
                print("❌ webSearch is NOT included in the request!")
            print("=" * 70 + "\n")

        # Call original function
        return original_post(url, **kwargs)

    # Patch requests.post
    import requests
    original_post = requests.post

    with patch('requests.post', side_effect=mock_post):
        try:
            # Get the model
            model = llm.get_model("1min/gpt-4o")

            # Try to execute (will fail without API key, but we'll see the request)
            try:
                result = model.prompt("tell me about https://www.sowitty.com")
                print("\nResponse:", result.text())
            except Exception as e:
                print(f"\nNote: API call failed (expected if no API key): {e}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    return web_search_sent


if __name__ == "__main__":
    print("Testing if web_search is sent to API...\n")

    # Show current config
    import llm_1min
    config = llm_1min.OptionsConfig()
    print("Current config:")
    print(json.dumps(config.load(), indent=2))
    print()

    was_sent = test_web_search_enabled()

    print("\n" + "=" * 70)
    if was_sent:
        print("✅ SUCCESS: web_search is being sent to the API")
    else:
        print("❌ PROBLEM: web_search is NOT being sent to the API")
    print("=" * 70)

    sys.exit(0 if was_sent else 1)
