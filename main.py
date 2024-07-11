import discord
import requests
from bs4 import BeautifulSoup as bs
import re
import os
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Tokens
tokens = open("token.txt", "r").readlines()
BOT_TOKEN = tokens[0].strip()
GEMINI_TOKEN = tokens[1].strip()

# Gemini
import google.generativeai as genai

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_instruction = open("system_instruction.txt", "r", encoding="utf-8").read()

genai.configure(api_key=GEMINI_TOKEN)

# Admin ID
ADMIN_ID = [784412272805412895, 742067560144437269]
MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)

# Discord Policy
intents = discord.Intents.default()
intents.message_content = True

# Funtions

def replace_emoji(inp: str) -> str:
    inp = re.sub(r'\[\[me\]\]', '<:me:1144858072624406588>', inp)
    inp = re.sub(r'\[\[star\]\]', '<:star:1144858244909633619>', inp)
    inp = re.sub(r'\[\[what\]\]', '<a:what:1144859308299923536>', inp)
    inp = re.sub(r'\[\[no\]\]', '<:no:1144857465566003253>', inp)
    inp = re.sub(r'\[\[hwal\]\]', '<:hwal:1144858220263907358>', inp)
    inp = re.sub(r'\[\[happy\]\]', '<:happy:1144857824866861056>', inp)
    inp = re.sub(r'\[\[grab\]\]', '<:grab:1144857312377446410>', inp)
    return inp

# Bot
client = discord.Bot(intents=intents)


@client.listen(once=True)
async def on_ready():
    print("Bot is ready!")
    activity = discord.Game(name="ONLINE")
    await client.change_presence(activity=activity)


@client.listen()
async def on_message(message):
    if message.content.startswith("ㄹ"):
        if message.author.id in ADMIN_ID:
            print(f"{message.author} [ADMIN] : {message.content[2:]}")
        else:
            print(f"{message.author} : {message.content[2:]}")

        ctx = message.content[2:].split()
        if ctx[0] == "핑":
            await message.channel.send(f"퐁! {round(client.latency * 1000)}ms")
        elif ctx[0] == "급식":
            url = "https://school.cbe.go.kr/daewon-h/M01061701/list"
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title="급식",
                    description="급식 정보를 가져오는데 실패했습니다.",
                    color=MAIN_COLOR,
                )
                await message.channel.send(embed=embed)
            else:
                soup = bs(response.text, "html.parser")
                times = soup.select("li.tch-lnc-wrap > dl > dt")
                menus = soup.select("li.tch-lnc-wrap > dl > dd > ul")
                menus_list = []
                times_list = []
                for i in times:
                    times_list.append(i.get_text())
                for i in menus:
                    menus_list.append(
                        list(
                            map(
                                lambda x: re.sub(r"\(.*?\)", "", x.get_text()).strip("\r*+ "),
                                i.select("li"),
                            )
                        )
                    )
                embed = discord.Embed(
                    title="급식", description="급식 정보입니다.", color=MAIN_COLOR
                )
                for i in range(len(times_list)):
                    embed.add_field(
                        name=times_list[i], value="\n".join(menus_list[i]), inline=False
                    )
                await message.channel.send(embed=embed)
        elif ctx[0] == "eval":
            if message.author.id in ADMIN_ID:
                try:
                    print(message.content[7:])
                    await message.channel.send(f"```{eval(message.content[7:])}```")
                except Exception as e:
                    await message.channel.send("```" + str(e) + "```")
            else:
                embed = discord.Embed(
                    title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "gemini":
            if len(message.content) != 8:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    generation_config=generation_config,
                    system_instruction=f"{system_instruction} 오늘의 날짜 및 시간은 {datetime.now()}입니다.",
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )

                chat_session = model.start_chat(history=[])

                response = chat_session.send_message(message.content[9:], stream=True)

                responses = ""
                for chunk in response:
                    if len(responses) == 0:
                        responses = replace_emoji(responses)
                        geminimsg = await message.channel.send(chunk.text)
                        responses += chunk.text
                    else:
                        responses += chunk.text
                        responses = replace_emoji(responses)
                        await discord.Message.edit(self=geminimsg, content=responses)
                    print(chunk.text, end='')

            else:
                embed = discord.Embed(
                    title="REBOT Gemini", description="내용을 입력하세요!", color=MAIN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "geminiprompt":
            if message.author.id in ADMIN_ID:
                await message.channel.send(
                    f"```{system_instruction} 오늘의 날짜 및 시간은 {datetime.now()}입니다.```"
                )
            else:
                embed = discord.Embed(
                    title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "테스트":
            await message.channel.send("<:grab:1144857312377446410>")


client.run(BOT_TOKEN)
