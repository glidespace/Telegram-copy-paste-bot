from telethon.errors import PhoneNumberBannedError, PasswordHashInvalidError, UsernameInvalidError
from telethon.types import DocumentAttributeFilename, InputMediaUploadedPhoto
from telethon.sync import TelegramClient, events
import os
import re

from config import (API_ID, API_HASH, PHONE_NUMBER, CHANNELS_COPY, CHANNEL_PASTE, DEVICE_MODEL,
                    SYSTEM_VERSION, AUTO_DELETE_LINKS, FORWARDS)

logo = """
█▀▀ █▀█ █▀█ █▄█ ▄▄ █▀█ ▄▀█ █▀ ▀█▀ █▀▀   █▄▄ █▀█ ▀█▀|ᵇʸ ᵈᵉˡᵃᶠᵃᵘˡᵗ
█▄▄ █▄█ █▀▀ ░█░ ░░ █▀▀ █▀█ ▄█ ░█░ ██▄   █▄█ █▄█ ░█░"""

def gd_print(value):
    green_color = '\033[32m'
    reset_color = '\033[0m'
    result = f"\n>{green_color} {value} {reset_color}\n"
    print(result)

def bd_print(value):
    red_color = '\033[31m'
    reset_color = '\033[0m'
    result = f"\n>{red_color} {value} {reset_color}\n"
    print(result)

async def check_caption(caption):
    if AUTO_DELETE_LINKS is False:
        return caption
    elif AUTO_DELETE_LINKS is True:
        return re.sub(r'<a\s[^>]*>.*?</a>', '', caption)
    elif AUTO_DELETE_LINKS is None:
        return re.sub(r'<a\s[^>]*>(.*?)</a>', r'\1', caption)
    elif AUTO_DELETE_LINKS not in [True, False, None]:
        return re.sub(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"(?:[^>]*)>(.*?)</a>', rf'<a href="{AUTO_DELETE_LINKS}">\2</a>', caption)

client = TelegramClient(
    session=f"tg_{PHONE_NUMBER}",
    api_id=API_ID,
    api_hash=API_HASH,
    device_model=DEVICE_MODEL,
    system_version=SYSTEM_VERSION
)

@client.on(events.NewMessage(CHANNELS_COPY, forwards=FORWARDS))
async def message_handler(event):
    """
    Handles new messages and maintains reply structure.
    """
    caption = event.message.text
    reply_to = None

    # Handle replies
    if event.message.is_reply:
        # Fetch the original message being replied to
        original_message = await event.message.get_reply_message()
        if original_message:
            # Search for the original message in the destination channel
            async for msg in client.iter_messages(CHANNEL_PASTE):
                if msg.text == original_message.text:
                    reply_to = msg.id
                    break

    caption = await check_caption(caption)

    # Process media and forward
    if event.message.photo:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.photo,
            caption=caption,
            reply_to=reply_to if reply_to else None
        )
    elif event.message.video:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.video,
            caption=caption,
            reply_to=reply_to if reply_to else None
        )
    elif event.message.document:
        await client.send_file(
            CHANNEL_PASTE,
            event.message.document,
            caption=caption,
            reply_to=reply_to if reply_to else None
        )
    else:
        await client.send_message(
            CHANNEL_PASTE,
            caption,
            reply_to=reply_to if reply_to else None
        )

    gd_print(f"Successfully forwarded message with reply-to: {reply_to}")

if __name__ == "__main__":
    try:
        client.start(phone=PHONE_NUMBER)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
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
