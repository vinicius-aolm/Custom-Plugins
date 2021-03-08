import asyncio
import random
from pyrogram import filters
from userge import Message, userge
@userge.on_cmd(
    "firstkill",
    about={
        "header": "Get first kill of the last werewolf game. Only works in @LobinhoRepublica.",
        "usage": "{tr}fk or wait to for the game to finish.",
    },
)
@userge.on_filters(
    (
        filters.chat(-1001199769918) &
        filters.regex("Tempo total do jogo|Duração da partida")
    ),
    allow_private=False,
    allow_channels=False
)
async def firstkill(message: Message):
    await message.reply("/candy_corn")


    














    #await message.edit(f"{(await userge.get_users(message.reply_to_message.from_user.id)).first_name} has: \n**1. IQ :** {random.choice(range(0,1000))}% \n**2. Dik Size :** {random.choice(range(0,10))} centimeter\n**3. Lie Meter Reading :** {random.choice(range(0,100))}% \n**4. Gey Count :** {random.choice(range(0,100))}%")
