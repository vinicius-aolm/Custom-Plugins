import re
from userge import userge, Message, filters

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
AFK = []
FIX = ""


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
    global AFK
    lines = message.text
    lines_count = len(lines.split("\n"))
    info = await message.reply("Obtendo FK.")
    try:
        deads = await build_list(lines)
        deads = [dead for dead in deads if dead not in AFK]
        AFK = []
        output = await order_fk(deads, lines_count)
        await info.edit(output)
    except:
        AFK = []
        await info.edit("Ocorreu um erro ao obter o FK.")


@userge.on_filters(
    (
        filters.chat(-1001199769918) &
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
    if players <= 7:
        first, evite = deads[0], ""  # 1 fk
        action = "1ª MORTE"
    elif players <= 10:
        first, evite = deads[0], deads[1]  # 1 fk, 1 evite
        action = "1ª FORCA"
    elif players <= 15:
        first, evite = "\n".join(deads[:1]), "\n".join(deads[2:3])  # 2 fk, 2 evite
        action = "1ª FORCA"
    else:
        first, evite = "\n".join(deads[:2]), "\n".join(deads[3:5])  # 3 fk, 3 evite
        action = "2ª FORCA"
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
        output = preout + posout
    else:
        output = preout
    return output
