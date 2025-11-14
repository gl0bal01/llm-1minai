#!/usr/bin/env python3
"""
Utility script to manage 1min.ai conversations.

This script provides commands to:
- List all conversations
- Delete specific conversations
- Clear all conversations
- Export conversation data

Usage:
    python manage_conversations.py list
    python manage_conversations.py delete <conversation_uuid>
    python manage_conversations.py clear --all
    python manage_conversations.py export
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

import requests


class ConversationManager:
    """Manage 1min.ai conversations via API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.1min.ai"
        self.headers = {"API-KEY": api_key, "Content-Type": "application/json"}

    def list_conversations(self) -> List[Dict]:
        """
        List all conversations.

        Returns:
            List of conversation objects
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/conversations", headers=self.headers, timeout=30
            )
            response.raise_for_status()
            return response.json().get("conversations", [])
        except requests.exceptions.RequestException as e:
            print(f"Error listing conversations: {e}", file=sys.stderr)
            return []

    def get_conversation(self, conversation_uuid: str) -> Optional[Dict]:
        """
        Get a specific conversation by UUID.

        Args:
            conversation_uuid: The conversation UUID

        Returns:
            Conversation object or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/conversations/{conversation_uuid}",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting conversation: {e}", file=sys.stderr)
            return None

    def delete_conversation(self, conversation_uuid: str) -> bool:
        """
        Delete a specific conversation.

        Args:
            conversation_uuid: The conversation UUID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/api/conversations/{conversation_uuid}",
                headers=self.headers,
                timeout=30,
            )
            return response.status_code in [200, 204, 404]
        except requests.exceptions.RequestException as e:
            print(f"Error deleting conversation: {e}", file=sys.stderr)
            return False

    def clear_all_conversations(self) -> int:
        """
        Delete all conversations.

        Returns:
            Number of conversations deleted
        """
        conversations = self.list_conversations()
        count = 0

        for conv in conversations:
            uuid = conv.get("uuid")
            if uuid and self.delete_conversation(uuid):
                count += 1

        return count

    def export_conversations(self, output_file: str = None) -> None:
        """
        Export all conversations to JSON file.

        Args:
            output_file: Optional output file path (default: conversations.json)
        """
        conversations = self.list_conversations()

        if output_file is None:
            output_file = "conversations.json"

        with open(output_file, "w") as f:
            json.dump(conversations, f, indent=2)

        print(f"Exported {len(conversations)} conversation(s) to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Manage 1min.ai conversations")
    parser.add_argument(
        "command", choices=["list", "get", "delete", "clear", "export"], help="Command to execute"
    )
    parser.add_argument("uuid", nargs="?", help="Conversation UUID (for get/delete commands)")
    parser.add_argument(
        "--all", action="store_true", help="Apply to all conversations (for clear command)"
    )
    parser.add_argument("--output", "-o", help="Output file for export command")
    parser.add_argument("--api-key", help="1min.ai API key (or set ONEMIN_API_KEY env var)")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("ONEMIN_API_KEY")
    if not api_key:
        print("Error: API key required. Set ONEMIN_API_KEY or use --api-key", file=sys.stderr)
        sys.exit(1)

    manager = ConversationManager(api_key)

    # Execute command
    if args.command == "list":
        conversations = manager.list_conversations()
        if not conversations:
            print("No conversations found")
        else:
            print(f"Found {len(conversations)} conversation(s):\n")
            for conv in conversations:
                print(f"UUID: {conv.get('uuid')}")
                print(f"  Title: {conv.get('title')}")
                print(f"  Type: {conv.get('type')}")
                print(f"  Model: {conv.get('model')}")
                print(f"  Created: {conv.get('createdAt')}")
                print()

    elif args.command == "get":
        if not args.uuid:
            print("Error: UUID required for 'get' command", file=sys.stderr)
            sys.exit(1)

        conv = manager.get_conversation(args.uuid)
        if conv:
            print(json.dumps(conv, indent=2))
        else:
            print(f"Conversation {args.uuid} not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "delete":
        if not args.uuid:
            print("Error: UUID required for 'delete' command", file=sys.stderr)
            sys.exit(1)

        if manager.delete_conversation(args.uuid):
            print(f"Deleted conversation {args.uuid}")
        else:
            print(f"Failed to delete conversation {args.uuid}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "clear":
        if not args.all:
            print("Error: Use --all flag to confirm clearing all conversations", file=sys.stderr)
            sys.exit(1)

        count = manager.clear_all_conversations()
        print(f"Cleared {count} conversation(s)")

    elif args.command == "export":
        manager.export_conversations(args.output)


if __name__ == "__main__":
    main()
