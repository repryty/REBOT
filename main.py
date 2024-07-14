import discord
import requests
from bs4 import BeautifulSoup as bs
import re
import os
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Tokens

# def get_token(name:str) -> str:
#     if os.path.isfile("/run/secrets/"+name):
#         with open("/run/secrets/"+name, "r", encoding="utf-8") as f:
#             return f.read().strip("\n")
#     else:
#         return os.environ[name]

BOT_TOKEN = os.getenv("REBOT_DISCORD_TOKEN")
GEMINI_TOKEN = os.getenv("REBOT_GEMINI_TOKEN")

# Gemini
import google.generativeai as genai

generation_config = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_instruction = open("system_instruction.txt", "r", encoding="utf-8").read()

genai.configure(api_key=GEMINI_TOKEN)

# Constants
ADMIN_ID = [784412272805412895, 742067560144437269]
MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)
WARN_COLOR = discord.Colour.from_rgb(181, 0, 0)

# Discord Policy
intents = discord.Intents.default()
intents.message_content = True

# Funtions

def replace_emoji(inp: str) -> str:
    inp = re.sub(r'🚪', '<:me:1144858072624406588>', inp)
    inp = re.sub(r'⭐', '<:star:1144858244909633619>', inp)
    inp = re.sub(r'❓', '<a:what:1144859308299923536>', inp)
    inp = re.sub(r'🚫', '<:no:1144857465566003253>', inp)
    inp = re.sub(r'🌸', '<:hwal:1144858220263907358>', inp)
    inp = re.sub(r'😊', '<:happy:1144857824866861056>', inp)
    inp = re.sub(r'✍🏼', '<:grab:1144857312377446410>', inp)
    inp = re.sub(r'😔', '<:hing:1144858197551759410>', inp)
    inp = re.sub(r'🫠', '<:liquid:1144857660836036609>', inp)
    inp = re.sub(r'😢', '<:sad:1144857284112040026>', inp)
    return inp

def make_time_instruction(system_instruction: str) -> str:
    return f"{system_instruction} 날짜, 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

async def signal(msg: str) -> None:
    print(msg)
    await client.get_channel(1261486436771823700).send(f"```{msg}```")

# Bot
client = discord.Bot(intents=intents)


@client.listen(once=True)
async def on_ready():
    activity = discord.Game(name="ONLINE")
    await client.change_presence(activity=activity)
    await signal("REBOT is online.")


@client.listen()
async def on_message(message):
    if message.content.startswith("ㄹ"):
        if message.author.id in ADMIN_ID:
            to_send=f"{message.author} [ADMIN] : {message.content[2:]}"
            await signal(to_send)
        else:
            await signal(f"{message.author} : {message.content[2:]}")

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
                    await signal(message.content[7:])
                    await message.channel.send(f"```{eval(message.content[7:])}```")
                except Exception as e:
                    await message.channel.send("```" + str(e) + "```")
            else:
                embed = discord.Embed(
                    title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "gemini":
            
            # if message.reference is not None: 
            #     chat_log = []
            #     current_message = message
            #     while current_message.reference is not None:
            #         # 참조된 메시지 ID를 사용하여 참조된 메시지를 가져옴
            #         referenced_message_id = current_message.reference.message_id
            #         channel = current_message.channel
            #         try:
            #             # 참조된 메시지를 가져옴
            #             current_message = await channel.fetch_message(referenced_message_id)
            #             # 메시지 체인에 추가
            #             chat_log.insert(0, current_message.content)
            #         except Exception as e:
            #             await signal(f"Error fetching message: {e}")
            #             break
            #     chat_log.append(message.content)
            #     message.reference.message_id
            #     await message.channel.send(chat_log)
            if len(message.content) != 8:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    generation_config=generation_config,
                    system_instruction=make_time_instruction(system_instruction),
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
                await signal(re.sub(r'`', '\\`', response.text))

            else:
                embed = discord.Embed(
                    title="REBOT Gemini", description="내용을 입력하세요!", color=WARN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "geminiprompt":
            if message.author.id in ADMIN_ID:
                await message.channel.send(
                    f"```{make_time_instruction(system_instruction)}```"
                )
            else:
                embed = discord.Embed(
                    title="REBOT eval", description="권한이 없습니다.", color=WARN_COLOR
                )
                await message.channel.send(embed=embed)
        elif ctx[0] == "요청":
            embed = discord.Embed(
                title="요청", description="개발중.", color=WARN_COLOR
            )
            await message.channel.send(embed=embed)


client.run(BOT_TOKEN)
