"""
Debug test to show exactly what's being sent in API requests with web_search.
Run this test with: pytest tests/test_web_search_debug.py -v -s
"""

import json
from unittest.mock import Mock, patch

import llm_1min


class TestWebSearchDebug:
    """Debug tests to show API payloads."""

    @patch("llm_1min.OneMinModel.get_key")
    def test_show_payload_with_web_search_from_config(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Show what payload looks like when web_search is set via config."""
        mock_get_key.return_value = "test-api-key"

        # Set web_search via config
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)
        config.set_option("num_of_site", 5)

        print("\n" + "=" * 60)
        print("CONFIG SETTINGS:")
        print(json.dumps(config.load(), indent=2))
        print("=" * 60)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            # Execute
            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Show the actual payload sent
            call_args = mock_post.call_args_list
            for i, call in enumerate(call_args):
                url = call[0][0]
                payload = call[1]["json"]
                print(f"\n{'=' * 60}")
                print(f"API CALL #{i+1}")
                print(f"URL: {url}")
                print("PAYLOAD:")
                print(json.dumps(payload, indent=2))
                print("=" * 60)

            # Verify
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            print("\n" + "=" * 60)
            print("VERIFICATION:")
            print(f"✓ webSearch in promptObject: {'webSearch' in payload['promptObject']}")
            if "webSearch" in payload["promptObject"]:
                print(f"✓ webSearch value: {payload['promptObject']['webSearch']}")
                print(f"✓ numOfSite value: {payload['promptObject']['numOfSite']}")
            print("=" * 60 + "\n")

            assert "webSearch" in payload["promptObject"]
            assert payload["promptObject"]["webSearch"] is True

    @patch("llm_1min.OneMinModel.get_key")
    def test_show_payload_without_web_search(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Show what payload looks like when web_search is NOT set."""
        mock_get_key.return_value = "test-api-key"

        print("\n" + "=" * 60)
        print("NO CONFIG SET (defaults)")
        print("=" * 60)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            # Show the actual payload
            call_args = mock_post.call_args_list
            features_call = [call for call in call_args if "features" in call[0][0]][0]
            payload = features_call[1]["json"]

            print(f"\n{'=' * 60}")
            print("API PAYLOAD:")
            print(json.dumps(payload, indent=2))
            print("=" * 60)

            print("\n" + "=" * 60)
            print("VERIFICATION:")
            print(f"✓ webSearch in promptObject: {'webSearch' in payload['promptObject']}")
            print("=" * 60 + "\n")

            assert "webSearch" not in payload["promptObject"]

    @patch("llm_1min.OneMinModel.get_key")
    def test_show_option_merging_priority(
        self, mock_get_key, mock_requests, mock_llm_prompt, mock_config_path
    ):
        """Show how options are merged: CLI > per-model > global."""
        mock_get_key.return_value = "test-api-key"

        # Set different values at different levels
        config = llm_1min.OptionsConfig()
        config.set_option("web_search", True)  # Global
        config.set_option("num_of_site", 3)  # Global
        config.set_option("num_of_site", 7, model_id="gpt-4o")  # Per-model override

        print("\n" + "=" * 60)
        print("CONFIG SETTINGS:")
        print(json.dumps(config.load(), indent=2))
        print("\nEXPECTED RESULT:")
        print("  - web_search: True (from global)")
        print("  - num_of_site: 7 (from per-model, overrides global 3)")
        print("=" * 60)

        model = llm_1min.OneMinModel("1min/gpt-4o", "gpt-4o", "GPT-4o")

        with patch("requests.post") as mock_post:
            mock_post.side_effect = mock_requests["post"]

            list(
                model.execute(
                    prompt=mock_llm_prompt, stream=False, response=Mock(), conversation=None
                )
            )

            features_call = [call for call in mock_post.call_args_list if "features" in call[0][0]][
                0
            ]
            payload = features_call[1]["json"]

            print("\n" + "=" * 60)
            print("ACTUAL RESULT:")
            print(f"  - webSearch: {payload['promptObject']['webSearch']}")
            print(f"  - numOfSite: {payload['promptObject']['numOfSite']}")
            print("=" * 60 + "\n")

            assert payload["promptObject"]["webSearch"] is True
            assert payload["promptObject"]["numOfSite"] == 7
