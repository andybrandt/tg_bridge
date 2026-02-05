% TG_BRIDGE(1) tg_bridge 0.3
% Andy Brandt
% February 2026

# NAME

tg_bridge - read-only Telegram channel bridge CLI for AI agents

# SYNOPSIS

**tg_bridge** [**-V**|**--version**] *command* [*options*]

**tg_bridge list**

**tg_bridge history** {**--channel** *name*|**--channel_id** *id*} **--after** *date* [**--limit** *n*]

**tg_bridge sync** {**--channel** *name*|**--channel_id** *id*} [**--limit** *n*]

**tg_bridge download** {**--channel** *name*|**--channel_id** *id*} **--message_id** *id* **--output** *dir*

# DESCRIPTION

**tg_bridge** is a read-only Telegram channel bridge designed for AI agents to consume Telegram channel messages. It connects to Telegram using the MTProto protocol via the Telethon library and outputs all data as JSON for machine parsing.

The tool supports incremental synchronization with persistent state tracking, allowing AI agents to efficiently poll for new messages without re-fetching historical data.

All operations are read-only; the tool never sends messages or modifies channel content.

# COMMANDS

**list**
:   List all Telegram channels accessible to the authenticated user. Returns an array of channel objects with **id**, **name**, and **username** fields.

**history**
:   Fetch messages from a channel starting after a specific date/time. Useful for one-time historical queries. Does not update sync state.

**sync**
:   Incremental synchronization that retrieves only new messages since the last sync. Automatically tracks and persists the last seen message ID per channel. This is the recommended command for regular polling.

**download**
:   Download a media attachment from a specific message. Supports photos, documents, videos, and audio files.

# OPTIONS

## Global Options

**-V**, **--version**
:   Display version information and exit.

## Channel Selection (required for history, sync, download)

**--channel** *name*
:   Channel username (without @) or display name.

**--channel_id** *id*
:   Numeric channel ID. Can be specified with or without the leading minus sign (both **-1001234567890** and **1001234567890** are accepted).

## Command-Specific Options

**--after** *date*
:   (history only, required) ISO 8601 formatted datetime to fetch messages after. Format: **YYYY-MM-DDTHH:MM:SS**

**--limit** *n*
:   (history, sync) Maximum number of messages to retrieve. Default: **50**

**--message_id** *id*
:   (download only, required) The numeric ID of the message containing the media to download.

**--output** *dir*
:   (download only, required) Directory path where the downloaded file will be saved. Created automatically if it does not exist.

# OUTPUT FORMAT

All output is JSON. Message objects contain:

- **id** - Numeric message ID
- **date** - ISO 8601 timestamp
- **sender** - Sender's numeric user ID
- **text** - Message text content (may be null for media-only messages)
- **media** - (optional) Media metadata object with **type**, **file_name**, **mime_type**, and **size**

Media types: **photo**, **document**, **video**, **audio**

Download command returns:

- **message_id** - The requested message ID
- **channel_id** - The channel's numeric ID
- **file_path** - Absolute path to the downloaded file
- **media_type** - Type of media downloaded
- **size** - File size in bytes

Errors are returned as: **{"error": "description"}**

# FILES

**~/.config/tg_bridge/**
:   Configuration directory (created automatically with mode 0700)

**~/.config/tg_bridge/session.session**
:   Telegram authentication session file. Created on first run after interactive authentication.

**~/.config/tg_bridge/channel_state.json**
:   Persistent sync state storing the last seen message ID for each channel. Used by the **sync** command.

# EXAMPLES

List all accessible channels:

    tg_bridge list

Get messages from a channel after a specific date:

    tg_bridge history --channel_id -1001234567890 --after 2026-01-15T00:00:00

Sync new messages (incremental):

    tg_bridge sync --channel MyChannel --limit 100

Download media from message 42:

    tg_bridge download --channel_id 1001234567890 --message_id 42 --output ./downloads

# FIRST RUN

On first execution, **tg_bridge** will prompt for interactive authentication:

1. Enter your phone number (international format)
2. Enter the verification code sent to your Telegram app
3. If enabled, enter your two-factor authentication password

The session is then persisted and subsequent runs require no interaction.

# EXIT STATUS

**0**
:   Success

**non-zero**
:   Error (details in JSON output)

# ENVIRONMENT

The tool does not use environment variables. API credentials are compiled into the binary.

# SEE ALSO

**jq**(1) for parsing JSON output

Project repository: https://github.com/abrandt/tg_bridge

# BUGS

Report bugs at: https://github.com/abrandt/tg_bridge/issues
