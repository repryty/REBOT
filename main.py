import discord
# from pycomcigan import TimeTable, get_school_code
import requests 
from bs4 import BeautifulSoup as bs
import re

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
            url="https://school.cbe.go.kr/daewon-h/M01061701/list?ymd=20240523"
            respone=requests.get(url)

            if respone.status_code==200:
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
token=open("token.txt","r").read()
client.run(token)