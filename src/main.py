import asyncio.selector_events
import discord
import os
import asyncio
import google.generativeai as genai

# Modules
from config import *
from commands import *

genai.configure(api_key=GEMINI_TOKEN)

# Discord Policy
intents = discord.Intents.default()
intents.message_content = True

# Bot
client = discord.Bot(intents=intents)
gemini=Gemini(generation_config=generation_config)
commands=Commands([], discord.Message, client, gemini)

async def gemini_worker():
    while True:
        # print(gemini.queue)
        try:
            for i in gemini.queue.keys():
                if len(gemini.queue[i])>0:
                    response, msg = await gemini.call(i)
                    if isinstance(response, str):
                        await signal(f"{gemini.sessions[i].model.model_name}, {response}")
                    else:
                        await msg.edit(content="", embed=response)
        except Exception as e:
            await signal(e)
        await asyncio.sleep(1)

async def signal(msg: str) -> None:
    print(msg)
    await client.get_channel(NOTICE_CHANNEL).send(f"```{msg}```")

@client.listen(once=True)
async def on_ready():
    activity = discord.Game(name="REBOT is online")
    await client.change_presence(activity=activity)
    await signal("REBOT is online.")
    await asyncio.sleep(1)
    activity = discord.Game(name="ㄹ 도움")
    await client.change_presence(activity=activity)
    for f in genai.list_files():
        f.delete()
    await gemini_worker()

@client.slash_command(name="핑", description="반응 지연시간을 측정합니다")
async def slash_ping(ctx: discord.ApplicationContext):
    is_admin=ctx.author.id in ADMIN_ID
    await signal(f"{ctx.author} [is_admin={is_admin}] : 핑")
    await ctx.send_response(await commands.commands_list["핑"]())

@client.slash_command(
    name="모델", 
    description="REEBOT Gemini의 모델을 변경합니다. 변경은 서버 전체에 반영됩니다."
    )
async def slash_model(ctx: discord.ApplicationContext, model: discord.Option(
            input_type=discord.SlashCommandOptionType.string,
            name="모델",
            choices=["pro", "flash", "proex"],
            required=True,
            description="사용할 모델",
            default="flash"
            )="flash"): # type: ignore
    commands.args=[model]
    commands.message=ctx
    response= await commands.commands_list["모델"]()
    return await ctx.send_response(embed=response)

@client.listen()
async def on_message(message: discord.Message):
    if not message.content.startswith("ㄹ "): return
    is_admin=message.author.id in ADMIN_ID
    await signal(f"{message.author} [is_admin={is_admin}] : {message.content[2:]}")

    args = message.content[2:].split()
    args.append(is_admin)
    if len(args)==2: commands.args=[None]+args[1:]
    else: commands.args=args[1:]
    commands.message=message
    if args[0] in commands.commands_list:
        try:
            content = await commands.commands_list[args[0]]()
            if isinstance(content, str):
                await message.channel.send(content)
            elif isinstance(content, discord.Embed):
                await message.channel.send(embed=content)
            else:
                await message.channel.send(file=content)
                os.remove(content.fp)
        except Exception as e:
            await signal(e)
    else:
        args.pop()
        # print(args)
        # await gemini_call(message)
        if gemini.queue.get(message.guild.id)==None:
            await gemini.reset(message.guild.id)
        geminimsg = await message.channel.send("<a:loading:1264015095223287878>")
        await gemini.push(message, message.guild.id, geminimsg)
        # await message.channel.send(gemini.queue)
        # response = await gemini.call(message.guild.id, geminimsg)
        # if isinstance(response, discord.Embed):
        #     await message.channel.send(embed=response)

client.run(BOT_TOKEN)