import re
import asyncio
from userge import userge, Message, filters

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
AFK = []
FIX = ""
CHAT = [-1001360580171, -1001199769918]


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
        filters.chat(CHAT) &
        filters.regex("Tempo total do jogo|Duração da partida")
    ),
    allow_private=False,
    allow_channels=False
)
async def auto_fk(message: Message):
    global AFK
    lines = message.text
    lines_count = len(lines.split("\n\n")[0].split("\n")) - 1
    info = await message.reply("Obtendo FK.")
    try:
        deads = await build_list(lines)
        deads = [dead for dead in deads if dead not in AFK]
        AFK = []
        output = await order_fk(deads, lines_count)
        await info.edit(output)
    except Exception as e:
        AFK = []
        await info.edit("Ocorreu um erro ao obter o FK.")
        await asyncio.sleep(5)
        await info.delete()
        await CHANNEL.log(f"{e}")


@userge.on_filters(
    (
        filters.chat(CHAT) &
        filters.regex("\(id:.*\)")
    ),
    allow_private=False,
    allow_channels=False
)
async def auto_afk(message: Message):
    global AFK
    lines = re.sub("🥇|🥉|🥈", "", message.text)
    afk = ["".join(re.findall("^.*\(id:.*\)", afk)) for afk in lines.split("\n")]
    afk = re.sub("\(id:.*\)", "", "".join(afk)).strip()
    AFK.append(afk)
 

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


async def order_fk(deads, players):
    dead_count = len(deads)
    if players <= 7 and dead_count >= 1:
        first = deads[0]
        evite = ""  # 1 fk
        action = "1ª MORTE"
    elif players <= 10 and dead_count >= 2:
        first = deads[0]
        evite = deads[1]  # 1 fk, 1 evite
        action = "1ª FORCA"
    elif players <= 15 and dead_count >= 4:
        first = "\n".join(deads[:2])
        evite = "\n".join(deads[2:4])  # 2 fk, 2 evite
        action = "1ª FORCA"
    elif players >= 16 and dead_count >= 6:
        first = "\n".join(deads[:3])
        evite = "\n".join(deads[3:6])  # 3 fk, 3 evite
        action = "2ª FORCA"
    else:
        output = "❌ Sem fk ❌ tenha senso."
        return output
    preout = (
        f"🚩 FK\n"
        f"{first}\n\n"
        f"VALE ATÉ A {action}!\n\n"
    )
    posout = (
        f"🐺 EVITE MATAR CEDO\n"
        f"{evite}\n\n"
    )
    if evite:
        output = preout + posout + FIX
    else:
        output = preout + FIX
    return output
