import asyncio
import random
from userge import Message, userge
@userge.on_cmd(
    "detail",
    about={
        "header": "detect details of user. Ignore measurement if you are Afrikan",
        "usage": "{tr}reply to detect details. Dont reply any Afrikans",
    },
)
async def detail_hi(message: Message):
  await message.edit(f"{(await userge.get_users(message.reply_to_message.from_user.id)).first_name} has: \n**1. IQ :** {random.choice(range(0,1000))}% \n**2. Dik Size :** {random.choice(range(0,10))} centimeter\n**3. Lie Meter Reading :** {random.choice(range(0,100))}% \n**4. Gey Count :** {random.choice(range(0,100))}%")
