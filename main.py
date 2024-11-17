from telethon.errors import PhoneNumberBannedError, PasswordHashInvalidError, UsernameInvalidError
from telethon.types import DocumentAttributeFilename
from telethon.sync import TelegramClient, events
import re

from config import (API_ID,
                    API_HASH,
                    PHONE_NUMBER,
                    CHANNELS_COPY,
                    CHANNEL_PASTE,
                    DEVICE_MODEL,
                    SYSTEM_VERSION,
                    AUTO_DELETE_LINKS,
                    FORWARDS)

logo = """
█▀▀ █▀█ █▀█ █▄█ ▄▄ █▀█ ▄▀█ █▀ ▀█▀ █▀▀   █▄▄ █▀█ ▀█▀|ᵇʸ ᵈᵉˡᵃᶠᵃᵘˡᵗ
█▄▄ █▄█ █▀▀ ░█░ ░░ █▀▀ █▀█ ▄█ ░█░ ██▄   █▄█ █▄█ ░█░"""

client = TelegramClient(
    session=f"tg_{PHONE_NUMBER}",
    api_id=API_ID,
    api_hash=API_HASH,
    device_model=DEVICE_MODEL,
    system_version=SYSTEM_VERSION
)

def gd_print(value):
    print(f"\033[32m{value}\033[0m")

def bd_print(value):
    print(f"\033[31m{value}\033[0m")

async def check_caption(caption):
    """Handles caption cleanup logic."""
    if AUTO_DELETE_LINKS is True:
        return re.sub(r'<a\s[^>]*>.*?</a>', '', caption)
    elif AUTO_DELETE_LINKS is None:
        return re.sub(r'<a\s[^>]*>(.*?)</a>', r'\1', caption)
    elif isinstance(AUTO_DELETE_LINKS, str):
        return re.sub(r'<a\s+href="[^"]*">(.*?)</a>', rf'<a href="{AUTO_DELETE_LINKS}">\1</a>', caption)
    return caption

@client.on(events.NewMessage(CHANNELS_COPY, forwards=FORWARDS))
async def message_handler(event):
    """Handles new messages and maintains reply structure."""
    caption = event.message.text
    reply_to = None

    # Handle replies
    if event.message.is_reply:
        original_message = await event.message.get_reply_message()
        if original_message:
            # Get the ID of the original message in the target channel
            reply_to = await client.get_messages(
                CHANNEL_PASTE,
                ids=original_message.id
            )

    caption = await check_caption(caption)

    if event.message.photo:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.photo,
            caption=caption,
            reply_to=reply_to.id if reply_to else None
        )
    elif event.message.video:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.video,
            caption=caption,
            reply_to=reply_to.id if reply_to else None
        )
    elif event.message.document:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.document,
            caption=caption,
            reply_to=reply_to.id if reply_to else None
        )
    else:
        await client.send_message(
            CHANNEL_PASTE,
            caption,
            reply_to=reply_to.id if reply_to else None
        )

if __name__ == "__main__":
    try:
        client.start(phone=PHONE_NUMBER)
        gd_print(f"Logged in as {PHONE_NUMBER}.")
        client.run_until_disconnected()
    except PhoneNumberBannedError:
        bd_print(f"Phone number {PHONE_NUMBER} is banned.")
    except PasswordHashInvalidError:
        bd_print("Invalid password.")
    except UsernameInvalidError:
        bd_print("Invalid username.")
    except Exception as e:
        bd_print(f"Error: {e}")
