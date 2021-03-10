import os
import ffmpeg
from pyrogram import emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pytgcalls import GroupCall

from userge import userge, Message, filters


VOICE_CHATS = {}


@userge.on_cmd(
    "join_vc",
    about={
        "header": "Join the current voice chat",
        "usage": "{tr}join_vc"
    }
)
async def join_voice_chat(client, message: Message):
    input_filename = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                  "input.raw")
    if message.chat.id in VOICE_CHATS:
        response = " Already Joined the Voice Chat"
        await update_userbot_message(message, message.text, response)
        return
    chat_id = message.chat.id
    group_call = GroupCall(client, input_filename)
    await group_call.start(chat_id, False)
    VOICE_CHATS[chat_id] = group_call
    response = " Joined the Voice Chat"
    await update_userbot_message(message, message.text, response)


@userge.on_cmd(
    "leave_vc",
    about={
        "header": "Leave the current voice chat",
        "usage": "{tr}leave_vc"
    }
)
async def leave_voice_chat(client, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    await group_call.stop()
    VOICE_CHATS.pop(chat_id, None)
    await update_userbot_message(message, message.text, " Left the Voice Chat")


@userge.on_cmd(
    "list_vc",
    about={
        "header": "List joined voice chats",
        "usage": "{tr}list_vc"
    }
)
async def list_voice_chat(client, message: Message):
    if not VOICE_CHATS:
        await update_userbot_message(
            message,
            message.text,
            " Didn't join any voice chat yet"
        )
        return
    vc_chats = ""
    for chat_id in VOICE_CHATS:
        chat = await client.get_chat(chat_id)
        vc_chats += f"- **{chat.title}**\n"
    await update_userbot_message(
        message,
        message.text,
        f" Currently joined:\n{vc_chats}"
    )


@userge.on_cmd(
    "stop",
    about={
        "header": "Stop",
        "usage": "{tr}stop"
    }
)
async def stop_playing(_, message: Message):
    group_call = VOICE_CHATS[message.chat.id]
    group_call.stop_playout()
    await update_userbot_message(message, message.text, " Stopped Playing")


@userge.on_cmd(
    "replay",
    about={
        "header": "Play the track from beginning",
        "usage": "{tr}replay"
    }
)
async def restart_playing(client, message: Message):
    input_filename = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                  "input.raw")
    if not VOICE_CHATS or message.chat.id not in VOICE_CHATS:
        group_call = GroupCall(client, input_filename)
        await group_call.start(message.chat.id, False)
        VOICE_CHATS[message.chat.id] = group_call
        await update_userbot_message(
            message,
            message.text,
            " Joined the Voice Chat and Playing from the Beginning..."
        )
        return
    group_call = VOICE_CHATS[message.chat.id]
    group_call.input_filename = input_filename
    group_call.restart_playout()
    await update_userbot_message(
        message,
        message.text,
        " Playing from the beginning..."
    )


@userge.on_cmd(
    "play",
    about={
        "header": "Reply to an audio to play it in current voice chat",
        "usage": "{tr}play"
    }
)
async def play_track(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        return
    input_filename = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                  "input.raw")
    audio = message.reply_to_message.audio
    status = "\n- Downloading audio file..."
    await update_userbot_message(message, message.text, status)
    audio_original = await message.reply_to_message.download()
    status += "\n- Transcoding..."
    await update_userbot_message(message, message.text, status)
    ffmpeg.input(audio_original).output(
        input_filename,
        format='s16le',
        acodec='pcm_s16le',
        ac=2, ar='48k'
    ).overwrite_output().run()
    os.remove(audio_original)
    try:
        async for m in client.search_messages(message.chat.id,
                                              filter="pinned",
                                              limit=1):
            if m.audio:
                await m.unpin()
        await message.reply_to_message.pin(True)
    except ChatAdminRequired:
        pass
    except FloodWait:
        pass
    if VOICE_CHATS and message.chat.id in VOICE_CHATS:
        status += f"\n- Playing **{audio.title}**..."
        await update_userbot_message(message, message.text, status)
    else:
        group_call = GroupCall(client, input_filename)
        await group_call.start(message.chat.id, False)
        VOICE_CHATS[message.chat.id] = group_call
        status += (
            f"\n- Joined the Voice Chat...\n- Playing **{audio.title}**..."
        )
        await update_userbot_message(message, message.text, status)


@userge.on_cmd(
    "mute",
    about={
        "header": "Mute the userbot in the current voice chat",
        "usage": "{tr}mute"
    }
)
async def mute(_, message: Message):
    group_call = VOICE_CHATS[message.chat.id]
    group_call.set_is_mute(True)
    await update_userbot_message(message, message.text, " Muted")


@userge.on_cmd(
    "unmute",
    about={
        "header": "Unmute the userbot in the current voice chat",
        "usage": "{tr}unmute"
    }
)
async def unmute(_, message: Message):
    group_call = VOICE_CHATS[message.chat.id]
    group_call.set_is_mute(False)
    await update_userbot_message(message, message.text, " Unmuted")


async def update_userbot_message(message: Message, text_user, text_bot):
    await message.edit_text(f"{emoji.SPEECH_BALLOON} `{text_user}`\n"
                            f"{emoji.ROBOT}{text_bot}")
