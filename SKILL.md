---
name: tg_bridge
description: Read Telegram channel messages and download media attachments
requires_binary: tg_bridge
---

# Telegram Channel Bridge

Use `tg_bridge` to read messages from Telegram channels. This is a **read-only** tool - it cannot send messages.

## Prerequisites

The tool must be authenticated. If you get authentication errors, inform the user they need to run `tg_bridge list` manually first to complete Telegram login.

## Commands

### List available channels

```bash
tg_bridge list
```

Returns JSON array of channels with `id`, `name`, and `username`.

### Get new messages (incremental sync)

```bash
tg_bridge sync --channel "Channel Name" --limit 50
tg_bridge sync --channel_id -1001234567890 --limit 50
```

Use `sync` for regular polling - it tracks the last seen message and only returns new ones. Prefer `--channel_id` when you have it (more reliable than names).

### Get messages after a date

```bash
tg_bridge history --channel "Channel Name" --after 2025-01-15T00:00:00 --limit 100
```

Use `history` for one-time queries or backfilling. Date is ISO 8601 format.

### Download media

```bash
tg_bridge download --channel_id -1001234567890 --message_id 12345 --output /tmp/downloads/
```

Downloads photo/video/document from a specific message. Returns JSON with `file_path` (absolute path to downloaded file).

## Output Format

All output is JSON. Messages include:

```json
{
  "id": 12345,
  "date": "2025-01-20T14:30:00+00:00",
  "sender": 987654321,
  "text": "Message content",
  "media": {
    "type": "photo",
    "file_name": "12345.jpg",
    "size": null
  }
}
```

The `media` field only appears if the message has an attachment. Media types: `photo`, `video`, `audio`, `document`.

## Typical Workflow

1. `tg_bridge list` - Find channel IDs
2. `tg_bridge sync --channel_id <id>` - Get new messages
3. If message has media you need: `tg_bridge download --channel_id <id> --message_id <msg_id> --output <dir>`

## Errors

Errors return: `{"error": "description"}`

Common errors:
- "Message X not found" - Invalid message ID
- "Message X has no media" - Tried to download from text-only message
- Authentication errors - User needs to re-authenticate manually
