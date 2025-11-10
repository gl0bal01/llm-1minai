#!/usr/bin/env python3
"""
Test script to verify 1min.ai API endpoint and response format.

This script helps identify the correct API endpoint structure and response format
before using the LLM plugin.

Usage:
    export ONEMIN_API_KEY="your-api-key"
    python test_api.py
"""

import os
import requests
import json


def test_api_endpoint(api_key, endpoint_url, test_streaming=True):
    """Test the 1min.ai API endpoint"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test payload - adjust based on actual API requirements
    payload = {
        "messages": [
            {"role": "user", "content": "Hello! Please respond with 'API is working'."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }

    print(f"Testing endpoint: {endpoint_url}")
    print(f"Request payload:\n{json.dumps(payload, indent=2)}\n")

    # Test non-streaming
    print("=" * 60)
    print("Testing NON-STREAMING response:")
    print("=" * 60)
    try:
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:\n{json.dumps(dict(response.headers), indent=2)}\n")

        if response.status_code == 200:
            result = response.json()
            print(f"Response Body:\n{json.dumps(result, indent=2)}\n")
        else:
            print(f"Error Response:\n{response.text}\n")

    except Exception as e:
        print(f"Error: {str(e)}\n")

    # Test streaming if requested
    if test_streaming:
        print("=" * 60)
        print("Testing STREAMING response:")
        print("=" * 60)

        payload["stream"] = True

        try:
            with requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30
            ) as r:
                print(f"Status Code: {r.status_code}\n")

                if r.status_code == 200:
                    print("Streaming chunks:")
                    for line in r.iter_lines():
                        if line:
                            decoded = line.decode('utf-8')
                            print(f"  {decoded}")

                else:
                    print(f"Error Response:\n{r.text}\n")

        except Exception as e:
            print(f"Error: {str(e)}\n")


def main():
    # Get API key from environment
    api_key = os.environ.get("ONEMIN_API_KEY")

    if not api_key:
        print("Error: ONEMIN_API_KEY environment variable not set")
        print("Usage: export ONEMIN_API_KEY='your-api-key' && python test_api.py")
        return

    # Test different possible endpoint URLs
    possible_endpoints = [
        "https://api.1min.ai/v1/chat/completions",
        "https://api.1min.ai/chat/completions",
        "https://api.1min.ai/api/v1/chat",
        "https://api.1min.ai/api/chat/completions",
        "https://api.1min.ai/v1/completions",
    ]

    print("Testing 1min.ai API endpoints")
    print("=" * 60)
    print()

    # Ask user which endpoint to test or test all
    print("Available endpoints to test:")
    for i, endpoint in enumerate(possible_endpoints, 1):
        print(f"  {i}. {endpoint}")
    print(f"  {len(possible_endpoints) + 1}. Test all endpoints")
    print(f"  {len(possible_endpoints) + 2}. Enter custom endpoint")

    try:
        choice = input(f"\nSelect endpoint to test (1-{len(possible_endpoints) + 2}): ").strip()

        if choice == str(len(possible_endpoints) + 1):
            # Test all endpoints
            for endpoint in possible_endpoints:
                print("\n" + "=" * 60)
                test_api_endpoint(api_key, endpoint, test_streaming=False)
        elif choice == str(len(possible_endpoints) + 2):
            # Custom endpoint
            custom_endpoint = input("Enter custom endpoint URL: ").strip()
            test_api_endpoint(api_key, custom_endpoint)
        else:
            # Test specific endpoint
            idx = int(choice) - 1
            if 0 <= idx < len(possible_endpoints):
                test_api_endpoint(api_key, possible_endpoints[idx])
            else:
                print("Invalid choice")

    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")


if __name__ == "__main__":
    main()
