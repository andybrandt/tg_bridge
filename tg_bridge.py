import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from telethon import TelegramClient
from telethon.utils import get_peer_id

# --- CONFIGURATION ---
API_ID = 38516606  # Replace with your API ID
API_HASH = '7e22c1f7c6fee703a0a72c8369c5fd46'
SESSION_NAME = 'ai_agent_session'
STATE_FILE = 'channel_state.json'

class DateTimeEncoder(json.JSONEncoder):
    """Helper to ensure datetime objects are JSON serializable."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def normalize_channel_id(channel_id_value):
    """
    Normalize a numeric channel ID so it works with or without a leading "-".
    """
    try:
        channel_id = int(channel_id_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Channel ID must be a numeric value.") from exc
    if channel_id > 0:
        return -channel_id
    return channel_id

def get_channel_state_key(entity):
    """
    Return a canonical channel key for state storage.
    This uses Telethon's peer ID which is stable across name/ID inputs.
    """
    return str(get_peer_id(entity))

async def main():
    parser = argparse.ArgumentParser(description="AI Telegram Bridge")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # 1. List Channels
    subparsers.add_parser('list', help="List available channels")

    # 2. History (Manual query by date)
    hist_parser = subparsers.add_parser('history', help="Get messages from a specific date")
    hist_channel_group = hist_parser.add_mutually_exclusive_group(required=True)
    hist_channel_group.add_argument('--channel', help="Channel username or name")
    hist_channel_group.add_argument('--channel_id', help="Numeric channel ID (with or without leading '-')")
    hist_parser.add_argument('--after', required=True, help="ISO format date (YYYY-MM-DDTHH:MM:SS)")
    hist_parser.add_argument('--limit', type=int, default=50, help="Max messages to retrieve")

    # 3. Sync (Get new since last check)
    sync_parser = subparsers.add_parser('sync', help="Get new messages since last checkpoint")
    sync_channel_group = sync_parser.add_mutually_exclusive_group(required=True)
    sync_channel_group.add_argument('--channel', help="Channel username or name")
    sync_channel_group.add_argument('--channel_id', help="Numeric channel ID (with or without leading '-')")
    sync_parser.add_argument('--limit', type=int, default=50, help="Max messages to retrieve")

    args = parser.parse_args()

    # Initialize Client (Read-Only approach: we never call send_message)
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    output = []

    try:
        if args.command == 'list':
            # Iterate over dialogs to find channels
            async for dialog in client.iter_dialogs():
                if dialog.is_channel:
                    output.append({
                        "id": dialog.id,
                        "name": dialog.name,
                        "username": getattr(dialog.entity, 'username', None)
                    })

        elif args.command == 'history':
            # Parse the provided date
            try:
                # Basic ISO parsing
                start_date = datetime.fromisoformat(args.after)
            except ValueError:
                print(json.dumps({"error": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}))
                return

            if args.channel_id:
                try:
                    channel_identifier = normalize_channel_id(args.channel_id)
                except ValueError as exc:
                    print(json.dumps({"error": str(exc)}))
                    return
            else:
                channel_identifier = args.channel
            entity = await client.get_entity(channel_identifier)
            
            # reverse=True fetches older messages to newer (chronological) if offset_date is used,
            # but usually iter_messages goes Newest -> Oldest. 
            # To get "After X", we iterate normally but stop when we hit the date.
            # Telethon's reverse=True combined with offset_date can be tricky.
            # Simpler approach for AI tool: Fetch N messages and filter in python or use offset_date.
            
            async for message in client.iter_messages(entity, limit=args.limit, offset_date=start_date, reverse=True):
                if message.text: # Only capture text messages
                    output.append({
                        "id": message.id,
                        "date": message.date,
                        "sender": message.sender_id,
                        "text": message.text
                    })

        elif args.command == 'sync':
            # Load state to find last read ID
            state = load_state()
            if args.channel_id:
                try:
                    channel_identifier = normalize_channel_id(args.channel_id)
                except ValueError as exc:
                    print(json.dumps({"error": str(exc)}))
                    return
            else:
                channel_identifier = args.channel

            entity = await client.get_entity(channel_identifier)
            channel_key = get_channel_state_key(entity)

            # Migrate any legacy keys (name or raw ID) to the canonical key.
            state_changed = False
            last_id = state.get(channel_key, 0)
            legacy_keys = [str(channel_identifier)]
            for legacy_key in legacy_keys:
                if legacy_key in state and legacy_key != channel_key:
                    legacy_last_id = state[legacy_key]
                    if legacy_last_id > last_id:
                        last_id = legacy_last_id
                    del state[legacy_key]
                    state_changed = True

            if state.get(channel_key, 0) != last_id:
                state[channel_key] = last_id
                state_changed = True
            
            new_last_id = last_id
            
            # min_id param fetches messages NEWER than that ID
            async for message in client.iter_messages(entity, limit=args.limit, min_id=last_id):
                if message.text:
                    output.append({
                        "id": message.id,
                        "date": message.date,
                        "sender": message.sender_id,
                        "text": message.text
                    })
                    # Update max ID seen
                    if message.id > new_last_id:
                        new_last_id = message.id
            
            # Save new state
            if new_last_id > last_id:
                state[channel_key] = new_last_id
                state_changed = True
            if state_changed:
                save_state(state)

    except Exception as e:
        output = {"error": str(e)}
    
    # Final Output for the AI
    print(json.dumps(output, cls=DateTimeEncoder, indent=2, ensure_ascii=False))

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())