# tg_bridge

A read-only Telegram channel bridge CLI tool designed for AI agents to consume Telegram channel messages. Outputs JSON for easy machine parsing.

## Features

- **List channels** - Enumerate all accessible channels
- **History query** - Fetch messages after a specific date/time
- **Incremental sync** - Track last read position per channel for efficient polling
- **Media support** - Extract metadata for photos, videos, audio, and documents
- **Download attachments** - Fetch media files from specific messages
- **JSON output** - All output is machine-readable JSON with UTF-8 support
- **Read-only by design** - Cannot send messages, only read

## Requirements

- Python 3.13+
- Telethon library
- Telegram API credentials (API ID and API Hash from [my.telegram.org](https://my.telegram.org))

## Installation

### System-wide installation (recommended for AI agents)

This method installs tg_bridge as an immutable system command that AI agents can use but not modify.

```bash
# Install Telethon system-wide
sudo pip install telethon

# Install the script
sudo cp tg_bridge.py /usr/local/bin/tg_bridge
sudo chmod 755 /usr/local/bin/tg_bridge
```

### Development installation

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

### API ID

The API_ID and API_HASH identify the app, not your account. You can leave them as is or relace them. Just please replace them if your fork this by any chance.

### First Run Authentication

**Important:** Before an AI agent can use tg_bridge, you must authenticate manually with your Telegram account. Run any command (e.g., `list`) and complete the interactive login:

```bash
tg_bridge list
# Enter your phone number when prompted
# Enter the verification code sent to your Telegram app
```

This only needs to be done once. The session persists until you log it out from Telegram app or delete the session file.

### Data Storage

All user data is stored in `~/.config/tg_bridge/`:

- `session.session` - Telegram authentication session
- `channel_state.json` - Sync state (last message ID per channel)

## Usage

### List available channels

```bash
tg_bridge list
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
tg_bridge history --channel "Channel Name" --after 2025-01-15T00:00:00 --limit 100

# By channel ID (more reliable)
tg_bridge history --channel_id 1001234567890 --after 2025-01-15T00:00:00
```

### Sync new messages (incremental)

```bash
# First sync fetches recent messages and saves checkpoint
tg_bridge sync --channel_id -1001234567890 --limit 50

# Subsequent syncs only return messages newer than last checkpoint
tg_bridge sync --channel_id -1001234567890
```

The sync state is persisted in `~/.config/tg_bridge/channel_state.json`.

### Download media attachments

```bash
# Download media from a specific message
tg_bridge download --channel_id -1001234567890 --message_id 12345 --output ./downloads/
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

## OpenClaw Integration

tg_bridge includes a skill file for [OpenClaw](https://openclaw.ai) AI agents.

### Installing the skill

```bash
mkdir -p ~/.openclaw/skills/tg_bridge
cp SKILL.md ~/.openclaw/skills/tg_bridge/
```

The skill provides:
- Automatic discovery when `tg_bridge` is in PATH
- Command documentation for the AI agent
- Workflow guidance for common tasks

### Typical AI agent workflow

1. `tg_bridge list` - Discover available channels
2. `tg_bridge sync --channel_id <id>` - Poll for new messages
3. `tg_bridge download ...` - Fetch media when needed

## License

MIT
