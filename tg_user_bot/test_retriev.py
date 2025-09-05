import logging

from datetime import UTC, datetime
from telethon import TelegramClient, events
from telethon.events.raw import EventBuilder

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def test_user_bot(tg_api_id: int, tg_api_hash: str, tg_phone: str, tg_login: str):
    timestamp = datetime.now(UTC)
    client = TelegramClient(f"test_user_bot_{timestamp}", tg_api_id, tg_api_hash)

    async def server_log_handler(event: EventBuilder):
        logging.info(event)

    client.add_event_handler(server_log_handler, events.NewMessage)
    client.run_until_disconnected()
