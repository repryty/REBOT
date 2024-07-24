import discord
from datetime import datetime
import discord.types
import discord.types.guild
import asyncio
import discord_actions
import config
from google_api import gemini_call

# Discord Policy
intents = discord.Intents.default()
intents.message_content = True


# Funtions


def make_time_instruction(system_instruction: str, is_pro: bool) -> str:
    if is_pro:
        return f"{system_instruction}. 날짜, 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. 현재 구동중인 AI모델은 Gemini 1.5 Pro입니다."
    else:
        return f"{system_instruction}. 날짜, 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. 현재 구동중인 AI모델은 Gemini 1.5 Flash입니다."


"""
async def web_parse(url: str) -> str:
    response = requests.get(url)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="다음 글을 최대한 요약하시오. ",
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    soup = bs(response.text, 'html.parser')
    gemini_response=model.start_chat().send_message(soup.get_text()).text
    await signal(f"{url} 처리 완료")
    return gemini_response
    # return soup.get_text()[:5000]
"""

# Bot
client = discord.Bot(intents=intents)

logger_target: discord.abc.Messageable = client.get_channel(1261486436771823700)  # type: ignore


async def signal(msg: str) -> None:
    print(msg)
    await logger_target.send(f"```{msg}```")


@client.listen(once=True)
async def on_ready():
    activity = discord.Game(name="REBOT is online")
    await client.change_presence(activity=activity)
    await signal("REBOT is online.")
    await asyncio.sleep(5)
    activity = discord.Game(name="ㄹ 도움")
    await client.change_presence(activity=activity)


# Message Functions


gemini_queue = {}


async def gemini_queue_call(message: discord.Message):
    gid: int = message.guild.id  # type: ignore
    if len(gemini_queue[gid]) != 0:
        await gemini_call(gemini_queue[gid].pop(0))


# Client
@client.slash_command(name="핑", description="반응 지연시간을 측정합니다")
async def ping(ctx):
    if ctx.author.id in config.ADMIN_ID:
        to_send = f"{ctx.author} [ADMIN] : /핑"
        is_admin = True
        await signal(to_send)
    else:
        await signal(f"{ctx.author} : /핑")
        is_admin = False
    content = await discord_actions.commands_list["핑"]([], "", is_admin)
    await ctx.respond(content)


@client.listen()
async def on_message(message: discord.Message):
    if not message.content.startswith("ㄹ "):
        return
    if message.author.id in config.ADMIN_ID:
        await signal(f"{message.author} [ADMIN] : {message.content[2:]}")
        is_admin = True
    else:
        await signal(f"{message.author} : {message.content[2:]}")
        is_admin = False

    args = message.content[2:].split()
    if args[0] in discord_actions.commands_list:
        response = await discord_actions.commands_list[args[0]](
            args[1:], message.content[2:], is_admin
        )
        if isinstance(response, str):
            await message.channel.send(response)
        elif isinstance(response, discord.Embed):
            await message.channel.send(embed=response)
        elif isinstance(response, discord.File):
            await message.channel.send(file=response)
        else:
            raise TypeError()
    else:
        await gemini_call(message)


client.run(config.BOT_TOKEN)
