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
    deads = await build_list(message.text)
    deads = "\n".join(deads)
    await message.reply(deads)


async def find_dead(line):
    name = re.sub("🥇|🥉|🥈", "", line)
    dead = "".join(re.findall("^.*: 💀", name))
    name = re.sub(": 💀", "", dead)
    return name


async def build_list(lines):
    deads = []
    for line in lines.split("\n"):
        name = await find_dead(line)
        if not name:
            continue
        deads.append(name)
    return deads
