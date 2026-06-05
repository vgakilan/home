# HomeQ Watch

`homeq_watch.py` polls the HomeQ search API for new listings, filters out anything already seen, and sends new matches to one or more Telegram chats.

## What it does

- Loads a HomeQ search payload from [`payload.json`](payload.json)
- Calls the HomeQ search endpoint
- Keeps only listings where `type == "individual"`
- Skips listings already recorded in [`seen.json`](seen.json)
- Sends any new listings to Telegram
- Persists the updated seen list back to [`seen.json`](seen.json)

## Requirements

- Python 3.10+ recommended
- A Telegram bot token
- One or more Telegram chat IDs

## Installation

1. Create and activate a virtual environment if you want to isolate dependencies.
2. Install the requirements:

```bash
pip install -r requirements.txt
```

## Configuration

The script reads environment variables from a local `.env` file or your shell environment.

Set these values:

- `TELEGRAM_BOT_TOKEN` - your Telegram bot token
- `TELEGRAM_CHAT_ID` - one chat ID or a comma-separated list of chat IDs

Example `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABCDEF_your_token_here
TELEGRAM_CHAT_ID=123456789,-1001234567890
```

## Search criteria

The HomeQ query lives in [`payload.json`](payload.json). In this repo it is configured to:

- randomize results
- prioritize first-come-first-served listings
- filter by price, room count, and area bounds
- exclude short leases
- sort by publish date descending

Edit that file to change the search behavior.

## Usage

Run the script directly:

```bash
python homeq_watch.py
```

If no new listings are found, the script prints:

```text
No new individual listings.
```

If new listings are found, it sends a Telegram message and updates `seen.json`.

## State file

[`seen.json`](seen.json) stores the IDs of listings that have already been notified. This prevents duplicate Telegram alerts across runs.

You can delete the file to make the script treat all matching listings as new again.

## Output format

Each Telegram message includes:

- title
- room count and area
- rent
- move-in date
- municipality and city
- short-lease flag
- direct HomeQ link

Messages are split automatically if they get too long for Telegram.

## Scheduling

This script is meant to be run on a schedule, for example with:

- Windows Task Scheduler
- cron
- a small VM or always-on machine

## Notes

- The script only sends listings where `type == "individual"`.
- Telegram previews are disabled to keep the messages compact.
- The HomeQ API response shape can change, so if HomeQ updates their API you may need to adjust the payload or formatting logic.
