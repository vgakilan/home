import json
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

HOMEQ_URL = "https://api.homeq.se/api/v3/search"
HOMEQ_BASE = "https://homeq.se"
STATE_FILE = "seen.json"

with open("payload.json", "r", encoding="utf-8") as f:
    PAYLOAD = json.load(f)

HEADERS = {"content-type": "application/json"}

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_IDS = [c.strip() for c in os.environ["TELEGRAM_CHAT_ID"].split(",") if c.strip()]

MAX_TG_LEN = 3900


def load_seen() -> set[int]:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_ids", []))
    except FileNotFoundError:
        return set()


def save_seen(seen: set[int]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "seen_ids": sorted(seen),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def fetch_results() -> list[dict]:
    r = requests.post(HOMEQ_URL, headers=HEADERS, json=PAYLOAD, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])


def yn(v: bool) -> str:
    return "Yes" if v else "No"


def format_item(it: dict) -> str:
    title = it.get("title", "")
    rooms = it.get("rooms")
    area = it.get("area")
    rent = it.get("rent")
    date_access = it.get("date_access", "")
    municipality = it.get("municipality", "")
    city = it.get("city", "")
    short_lease = yn(bool(it.get("is_short_lease")))
    uri = it.get("uri", "")
    link = f"{HOMEQ_BASE}{uri}" if uri else ""

    parts = [
        title,
        f"{rooms} rum • {area} m²" if rooms and area else "",
        f"Rent: {rent} kr" if rent else "",
        f"Move-in: {date_access}" if date_access else "",
        f"Area: {municipality} / {city}".strip(" /") if municipality or city else "",
        f"Short lease: {short_lease}",
        link,
    ]
    return "\n".join(p for p in parts if p)


def send_telegram(chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for i in range(0, len(text), MAX_TG_LEN):
        payload = {
            "chat_id": chat_id,
            "text": text[i:i + MAX_TG_LEN],
            "disable_web_page_preview": True,
        }
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()


def main():
    seen = load_seen()
    results = fetch_results()

    results = [it for it in results if it.get("type") == "individual"]

    new_items = []
    for it in results:
        pid = it.get("id")
        if isinstance(pid, int) and pid not in seen:
            new_items.append(it)

    if not new_items:
        print("No new individual listings.")
        return

    for it in new_items:
        seen.add(it["id"])
    save_seen(seen)

    msg = "HomeQ: new listings\n\n" + "\n\n---\n\n".join(
        format_item(it) for it in new_items
    )

    for chat_id in CHAT_IDS:
        send_telegram(chat_id, msg)

    print(f"Sent {len(new_items)} new listings to {len(CHAT_IDS)} chat(s).")


if __name__ == "__main__":
    main()
