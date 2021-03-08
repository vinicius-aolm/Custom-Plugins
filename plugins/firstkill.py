import re
from userge import userge, Message, filters

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "firstkill",
    about={
        "header": "Get first kill of the last werewolf game. Only works in @LobinhoRepublica.",
        "usage": "{tr}fk or wait for the game to finish.",
    },
)
async def firstkill(message: Message):
    pass


@userge.on_filters(
    (
        filters.chat(-1001199769918) &
        filters.regex("Tempo total do jogo|Duração da partida")
    ),
    allow_private=False,
    allow_channels=False
)
async def auto_fk(message: Message):
    msg = message.reply("Obtendo FK.")
    deads = "\n".join(await format_fk(message))
    await msg.edit(deads)


async def format_fk(message):
    text = re.sub("🥇|🥉|🥈", "", message.text)
    deads = [re.findall("^.*: 💀", dead) for dead in text.split("\n")]
    names = []
    for dead in deads:
        unformatted = "".join(dead)
        names.append(re.sub(": 💀", "", unformatted))
    return names
