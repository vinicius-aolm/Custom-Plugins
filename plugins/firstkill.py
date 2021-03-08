import re
import asyncio
from userge import userge, Message, filters

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
AFK = []
FIX = ""
FK = ""
CHAT = [-1001199769918]
WW = [1029642148, 980444671, 618096097, 175844556, 738172950, 1569645653]  # werewolf bots and testers


@userge.on_filters(
    (
        filters.command("fk") &
        filters.chat(CHAT) &
        ~filters.bot
    )
)
async def firstkill(message: Message):
    if FK:
        await message.reply(FK)
    elif await is_sr(message):
        await message.reply("❌ Sem Regras, Sem FK ❌ Tenha Senso")
    else:
        await message.reply("❌ Sem FK ❌")


@userge.on_filters(
    (
        filters.chat(CHAT) &
        filters.user(WW) &
        filters.regex("Tempo total do jogo|Duração da partida")
    )
)
async def auto_fk(message: Message):
    global AFK
    global FK
    if await is_sr(message):
        return
    lines = message.text
    lines_count = len(lines.split("\n\n")[0].split("\n")) - 1
    info = await userge.send_message(message.chat.id, "Obtendo FK.")
    try:
        deads = await build_list(lines)
        deads = [dead for dead in deads if dead not in AFK]
        output = await order_fk(deads, lines_count)
        await info.edit(output)
        FK = output
    except Exception as e:
        await info.edit("Ocorreu um erro ao obter o FK.")
        await asyncio.sleep(5)
        await info.delete()
        await CHANNEL.log(f"{e}")
        FK = ""
    AFK = []


@userge.on_filters(
    (
        filters.chat(CHAT) &
        filters.user(WW) &
        filters.regex("\(id:.*\)")
    )
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
    br = "\n"
    if players <= 7:
        sl_first = slice(1)
        first = br.join(deads[sl_first])
        evite = ""  # 1 fk
        action = "1ª MORTE"
    elif players <= 10:
        sl_first, sl_evite = slice(1), slice(1, 2)
        first = br.join(deads[sl_first])
        evite = br.join(deads[sl_evite])  # 1 fk, 1 evite
        action = "1ª FORCA"
    elif players <= 15:
        sl_first, sl_evite = slice(2), slice(2, 4)
        first = br.join(deads[sl_first])
        evite = br.join(deads[sl_evite])  # 2 fk, 2 evite
        action = "1ª FORCA"
    elif players >= 16:
        sl_first, sl_evite = slice(3), slice(3, 6)
        first = br.join(deads[sl_first])
        evite = br.join(deads[sl_evite])  # 3 fk, 3 evite
        action = "2ª FORCA"
    else:
        output = "O FK é... ninguém."
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


async def is_sr(message):
    title = message.chat.title
    sr = re.findall("SEM REGRAS", title)
    if sr:
        return True
