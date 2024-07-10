import discord
# from pycomcigan import TimeTable, get_school_code
import requests 
from bs4 import BeautifulSoup as bs
import re
import os

# Gemini
import google.generativeai as genai
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)




genai.configure(api_key="AIzaSyAZlEp9icdngXela5XyTBCTF1AbQEOHn-g")

ADMIN_ID=[784412272805412895]
MAIN_COLOR=discord.Colour.from_rgb(34, 75, 176)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Bot(intents=intents)

@client.listen(once=True)
async def on_ready():
    print("Bot is ready!")
    activity = discord.Game(name="ONLINE")
    await client.change_presence(activity=activity)

@client.listen()
async def on_message(message):
    if message.content.startswith("ㄹ"):
        ctx=message.content[2:].split()
        if ctx[0] == "핑":
            await message.channel.send(f"퐁! {round(client.latency*1000)}ms")
        # elif message.content[2:] == "시간표":
        #     timetable = TimeTable("충주대원고등학교")
        #     await message.channel.send(timetable.timetable)
        elif ctx[0] == "급식":
            url="https://school.cbe.go.kr/daewon-h/M01061701/list"
            try:
                respone=requests.get(url)
            except:
                embed = discord.Embed(title="급식", description="급식 정보를 가져오는데 실패했습니다.", color=MAIN_COLOR)
                await message.channel.send(embed=embed)
            else:
                soup=bs(respone.text,"html.parser")
                times=soup.select("li.tch-lnc-wrap > dl > dt")
                menus=soup.select("li.tch-lnc-wrap > dl > dd > ul")
                menus_list=[]
                times_list=[]
                for i in times:
                    times_list.append(i.get_text())
                for i in menus:
                    menus_list.append(list(map(lambda x: re.sub(r"\(.*?\)", "", x.get_text()).strip("\r*+ "), i.select("li"))))
                # await message.channel.send(f"```{times_list}, {menus_list}```")
                embed = discord.Embed(title="급식", description="급식 정보입니다.", color=MAIN_COLOR)
                for i in range(len(times_list)):
                    embed.add_field(name=times_list[i], value="\n".join(menus_list[i]), inline=False)
                await message.channel.send(embed=embed)
        elif ctx[0] == "eval":
            if message.author.id in ADMIN_ID:
                try:
                    await message.channel.send(f"```{eval(message.content[6:])}```")
                except Exception as e:
                    await message.channel.send("```"+str(e)+"```")
            else:
                embed=discord.Embed(title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR)
                await message.channel.send(embed=embed)
        elif ctx[0] == "gemini":
            chat_session = model.start_chat(
                history=[
                ]
            )

            response = chat_session.send_message(message.content[9:])

            await message.channel.send(response.text)
            
token=open("token.txt","r").read()
client.run(token)