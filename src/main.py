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
gemini=Gemini(generation_config=generation_config, system_instruction=system_instruction)
commands=Commands([], discord.Message, client, gemini)

async def gemini_worker():
    while True:
        # print(gemini.queue)
        for i in gemini.queue.keys():
            if len(gemini.queue[i])>0:
                response, msg = await gemini.call(i)
                if isinstance(response, str):
                    await signal(response)
                else:
                    await msg.edit(content="", embed=response)

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
    await gemini_worker()

@client.listen()
async def on_message(message: discord.Message):
    if not message.content.startswith("ㄹ "): return
    is_admin=message.author.id in ADMIN_ID
    await signal(f"{message.author} [is_admin={is_admin}] : {message.content[2:]}")

    args = message.content[2:].split()
    args.append(is_admin)
    commands.args=args[1:]
    commands.message=message
    if args[0] in commands.commands_list:
        content = await commands.commands_list[args[0]]()
        if isinstance(content, str):
            await message.channel.send(content)
        elif isinstance(content, discord.Embed):
            await message.channel.send(embed=content)
        else:
            await message.channel.send(file=content)
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