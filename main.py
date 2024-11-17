from telethon.errors import PhoneNumberBannedError, PasswordHashInvalidError, UsernameInvalidError
from telethon.types import DocumentAttributeFilename, InputMediaUploadedPhoto
from telethon.sync import TelegramClient, events
import os
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

last_id_message = []
id_mapping = {}  # Maps {source_message_id: destination_message_id}

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

@client.on(events.Album(CHANNELS_COPY))
async def album_handler(event):
    """
    Handles albums
    """
    if FORWARDS is True:
        if event.messages[0].fwd_from:
            pass
        else:
            return
    elif FORWARDS is False:
        if event.messages[0].fwd_from:
            return

    media = []
    caption = event.messages[0].text
    force_document = False
    id = event.messages[0].id
    if id in last_id_message:
        last_id_message.clear()
        return  # Album sometimes triggers the same event twice for a single message.
    last_id_message.append(id)

    caption = await check_caption(caption)

    gd_print(f"Received an album of {len(event)} messages.")

    for group_message in event.messages:
        if group_message.photo:
            media.append(await client.download_media(group_message, f"temp_pics/{group_message.id}.png"))
        elif group_message.video:
            media.append(await client.download_media(group_message, f"temp_pics/{group_message.id}.mp4"))
        elif group_message.document:
            file_name = next((x.file_name for x in group_message.document.attributes if isinstance(x, DocumentAttributeFilename)), None)
            media.append(await client.download_media(group_message, f"temp_pics/{file_name}"))
            force_document = True
        else:
            return bd_print("Unknown message type")

    sent_message = await client.send_file(CHANNEL_PASTE, media, caption=caption, force_document=force_document)
    gd_print(f"Successfully copied an album of {len(event)} messages.")

    for file in media:
        os.remove(file)  # Use a temporary folder for convenience.

    # Map the source message ID to the destination message ID
    id_mapping[id] = sent_message.id

@client.on(events.NewMessage(CHANNELS_COPY, forwards=FORWARDS))
async def message_handler(event):
    """
    Handles messages
    """
    if event.message.grouped_id is not None:
        return

    id = event.message.id
    caption = event.message.text
    spoiler = False
    web_preview = False

    try:
        if event.message.media.__dict__.get('spoiler') is True:
            spoiler = True
    except (AttributeError, KeyError):
        pass

    try:
        if event.message.media.webpage.__dict__.get('url') is not None:
            web_preview = True
    except (AttributeError, KeyError):
        pass

    gd_print(f"Processing message {id}.")

    # Check if the message is a reply
    reply_to = None
    if event.message.is_reply:
        original_message = await event.message.get_reply_message()
        if original_message and original_message.id in id_mapping:
            reply_to = id_mapping[original_message.id]  # Get the mapped ID

    caption = await check_caption(caption)

    # Sending media
    if event.message.photo and not web_preview:
        file_path = f"temp_pics/pics_{id}.png"
        await client.download_media(event.message, file_path)
        sent_message = await client.send_file(CHANNEL_PASTE, InputMediaUploadedPhoto(
            await client.upload_file(file_path), spoiler=spoiler), caption=caption, reply_to=reply_to)
        os.remove(file_path)

    elif event.message.video:
        file_path = f"temp_pics/pics_{id}.mp4"
        await client.download_media(event.message, file_path)
        sent_message = await client.send_file(CHANNEL_PASTE, file_path, caption=caption, video_note=True, reply_to=reply_to)
        os.remove(file_path)

    elif event.message.document:
        file_name = next((x.file_name for x in event.message.document.attributes if isinstance(x, DocumentAttributeFilename)), None)
        file_path = f"temp_pics/{file_name}"
        await client.download_media(event.message, file_path)
        sent_message = await client.send_file(CHANNEL_PASTE, file_path, caption=caption, force_document=True, reply_to=reply_to)
        os.remove(file_path)

    else:
        sent_message = await client.send_message(CHANNEL_PASTE, caption, reply_to=reply_to)

    # Map the source message ID to the destination message ID
    id_mapping[id] = sent_message.id
    gd_print(f"Message {id} copied to {sent_message.id} in destination channel.")

if __name__ == "__main__":
    try:
        client.start(phone=PHONE_NUMBER)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        gd_print(f"Successfully logged in with account {PHONE_NUMBER}.")
        client.parse_mode = "html"

        client.run_until_disconnected()
        gd_print(f"Session {PHONE_NUMBER} ended.")
    except PhoneNumberBannedError:
        bd_print(f"Account {PHONE_NUMBER} is banned.")
    except PasswordHashInvalidError:
        bd_print(f"Invalid password for account {PHONE_NUMBER}.")
    except UsernameInvalidError:
        pass
    except Exception as e:
        bd_print(f"Unknown error: {e}")
