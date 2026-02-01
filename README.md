# tg_bridge

A read-only Telegram channel bridge CLI tool designed for AI agents to consume Telegram channel messages. Outputs JSON for easy machine parsing.

## Features

- **List channels** - Enumerate all accessible channels
- **History query** - Fetch messages after a specific date/time
- **Incremental sync** - Track last read position per channel for efficient polling
- **Media support** - Extract metadata for photos, videos, audio, and documents
- **Download attachments** - Fetch media files from specific messages
- **JSON output** - All output is machine-readable JSON with UTF-8 support

## Requirements

- Python 3.13+
- Telegram API credentials (API ID and API Hash from [my.telegram.org](https://my.telegram.org))

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd tg_bridge

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install telethon
```

## Configuration

Edit `tg_bridge.py` and replace the API credentials:

```python
API_ID = 12345678          # Your API ID
API_HASH = 'your_api_hash' # Your API Hash
```

On first run, you'll be prompted to authenticate with your phone number. The session is saved to `ai_agent_session.session`.

## Usage

### List available channels

```bash
python tg_bridge.py list
```

Output:
```json
[
  {"id": -1001234567890, "name": "Channel Name", "username": "channeluser"},
  {"id": -1009876543210, "name": "Another Channel", "username": null}
]
```

### Get messages after a specific date

```bash
# By channel name/username
python tg_bridge.py history --channel "Channel Name" --after 2025-01-15T00:00:00 --limit 100

# By channel ID
python tg_bridge.py history --channel_id 1001234567890 --after 2025-01-15T00:00:00
```

### Sync new messages (incremental)

```bash
# First sync fetches recent messages and saves checkpoint
python tg_bridge.py sync --channel "Channel Name" --limit 50

# Subsequent syncs only return messages newer than last checkpoint
python tg_bridge.py sync --channel "Channel Name"
```

The sync state is persisted in `channel_state.json`.

### Download media attachments

```bash
# Download media from a specific message
python tg_bridge.py download --channel "Channel Name" --message_id 12345 --output ./downloads/

# Using channel ID
python tg_bridge.py download --channel_id 1001234567890 --message_id 12345 --output ./downloads/
```

## Output Format

All commands output JSON. Message objects include:

```json
{
  "id": 12345,
  "date": "2025-01-20T14:30:00+00:00",
  "sender": 987654321,
  "text": "Message content here"
}
```

Messages with media attachments include a `media` field:

```json
{
  "id": 12346,
  "date": "2025-01-20T14:35:00+00:00",
  "sender": 987654321,
  "text": "Check out this document!",
  "media": {
    "type": "document",
    "file_name": "report.pdf",
    "mime_type": "application/pdf",
    "size": 1048576
  }
}
```

Supported media types: `photo`, `video`, `audio`, `document`

Messages with only media (no text) are included with `text` as an empty string.

Download command returns:

```json
{
  "message_id": 12346,
  "channel_id": -1001234567890,
  "file_path": "/absolute/path/to/report.pdf",
  "media_type": "document",
  "size": 1048576
}
```

Errors are returned as:
```json
{"error": "Error description"}
```

## License

MIT
