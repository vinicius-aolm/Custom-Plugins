import os
import ffmpeg

from pytgcalls import GroupCall
from userge import userge, filters, Message


group_call = GroupCall(None, path_to_log_file="")


def init_client_and_delete_message(func):
    async def wrapper(message):
        group_call.client = userge
        await message.delete()
        return await func(message)
    return wrapper


@userge.on_cmd(
    "play",
    about={
        "header": "Reply to an audio to play it in current voice chat",
        "usage": "{tr}play",
    },
)
async def start_playout(message: Message):
    group_call.client = userge
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.delete()
        return
    input_filename = "input.raw"
    status = "- Downloading... \n"
    await message.edit_text(status)
    audio_original = await message.reply_to_message.download()
    status += "- Converting... \n"
    ffmpeg.input(audio_original).output(
        input_filename, format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(audio_original)
    status += f"- Playing **{message.reply_to_message.audio.title}**..."
    await message.edit_text(status)
    group_call.input_filename = input_filename


@userge.on_cmd(
    "volume",
    about={
        "header": "Set the volume of the bot in the voice chat",
        "usage": "{tr}volume <1-200>",
    },
)
@init_client_and_delete_message
async def volume(message: Message):
    if len(message.command) < 2:
        await message.reply_text("You forgot to pass volume (1-200)")
    await group_call.set_my_volume(message.command[1])


@userge.on_cmd(
    "join_vc",
    about={
        "header": "Join the current voice chat",
        "usage": "{tr}join_vc"
    },
)
@init_client_and_delete_message
async def start(message: Message):
    await group_call.start(message.chat.id, False)


@userge.on_cmd(
    "leave_vc",
    about={
        "header": "Leave the current voice chat",
        "usage": "{tr}leave_vc"
    },
)
@init_client_and_delete_message
async def stop(message: Message):
    await group_call.stop()


@userge.on_cmd(
    "rejoin",
    about={
        "header": "Rejoin the current voice chat",
        "usage": "{tr}rejoin"
    },
)
@init_client_and_delete_message
async def reconnect(message: Message):
    await group_call.reconnect()


@userge.on_cmd(
    "replay",
    about={
        "header": "Play the track from beginning",
        "usage": "{tr}replay"
    },
)
@init_client_and_delete_message
async def restart_playout(message: Message):
    group_call.restart_playout()


@userge.on_cmd(
    "stop",
    about={
        "header": "Stop the current playing track",
        "usage": "{tr}stop"
    },
)
@init_client_and_delete_message
async def stop_playout(message: Message):
    group_call.stop_playout()


@userge.on_cmd(
    "mute_vc",
    about={
        "header": "Mute the userbot in the current voice chat",
        "usage": "{tr}mute_vc",
    },
)
@init_client_and_delete_message
async def mute(message: Message):
    group_call.set_is_mute(True)


@userge.on_cmd(
    "unmute_vc",
    about={
        "header": "Unmute the userbot in the current voice chat",
        "usage": "{tr}unmute_vc",
    },
)
@init_client_and_delete_message
async def unmute(message: Message):
    group_call.set_is_mute(False)
