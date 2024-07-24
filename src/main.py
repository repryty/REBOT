import discord
from discord import default_permissions
import requests
from bs4 import BeautifulSoup as bs
import re
import os
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import PIL.Image
import time
import asyncio

# Tokens
BOT_TOKEN = os.getenv("REBOT_DISCORD_TOKEN")
GEMINI_TOKEN = os.getenv("REBOT_GEMINI_TOKEN")
NEIS_TOKEN = os.getenv("REBOT_NEIS_TOKEN")
GOOGLE_TOKEN = os.getenv("REBOT_GOOGLE_TOKEN")

# Gemini
import google.generativeai as genai

generation_config: genai.types.GenerationConfigDict = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}  # type: ignore

with open("prompts/system_instruction.txt", "r", encoding="utf-8") as f:
    system_instruction = f.read()

genai.configure(api_key=GEMINI_TOKEN)

chat_session = dict()

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

# Constants
ADMIN_ID = [784412272805412895, 742067560144437269]
MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)
WARN_COLOR = discord.Colour.from_rgb(181, 0, 0)

# Discord Policy
intents = discord.Intents.default()
intents.message_content = True


# Funtions


def replace_emoji(inp: str) -> str:
    inp = re.sub(r"🚪", "<:me:1144858072624406588>", inp)
    inp = re.sub(r"⭐", "<:star:1144858244909633619>", inp)
    inp = re.sub(r"❓", "<a:what:1144859308299923536>", inp)
    inp = re.sub(r"🚫", "<:no:1144857465566003253>", inp)
    inp = re.sub(r"🌸", "<:hwal:1144858220263907358>", inp)
    inp = re.sub(r"😊", "<:happy:1144857824866861056>", inp)
    inp = re.sub(r"✍🏼", "<:grab:1144857312377446410>", inp)
    inp = re.sub(r"😔", "<:hing:1144858197551759410>", inp)
    inp = re.sub(r"🫠", "<:liquid:1144857660836036609>", inp)
    inp = re.sub(r"😢", "<:sad:1144857284112040026>", inp)
    # inp = re.sub(r'([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF])', "", inp)
    return inp


def make_time_instruction(system_instruction: str, is_pro: bool) -> str:
    if is_pro:
        return f"{system_instruction}. 날짜, 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. 현재 구동중인 AI모델은 Gemini 1.5 Pro입니다."
    else:
        return f"{system_instruction}. 날짜, 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. 현재 구동중인 AI모델은 Gemini 1.5 Flash입니다."


async def signal(msg: str) -> None:
    print(msg)
    await client.get_channel(1261486436771823700).send(f"```{msg}```")


def google_search(ctx: str) -> list:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_TOKEN, "cx": "12e5fcf523c684260", "q": ctx}
    response = requests.get(url, params)
    items = [i["title"] for i in response.json()["items"]]
    links = [i["link"] for i in response.json()["items"]]
    return [items, links]


# async def web_parse(url: str) -> str:
#     response = requests.get(url)
#     model = genai.GenerativeModel(
#         model_name="gemini-1.5-flash",
#         generation_config=generation_config,
#         system_instruction="다음 글을 최대한 요약하시오. ",
#         safety_settings={
#             HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#             HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#             HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#             HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#         }
#     )
#     soup = bs(response.text, 'html.parser')
#     gemini_response=model.start_chat().send_message(soup.get_text()).text
#     await signal(f"{url} 처리 완료")
#     return gemini_response
#     # return soup.get_text()[:5000]

# Bot
client = discord.Bot(intents=intents)


@client.listen(once=True)
async def on_ready():
    activity = discord.Game(name="REBOT is online")
    await client.change_presence(activity=activity)
    await signal("REBOT is online.")
    await asyncio.sleep(5)
    activity = discord.Game(name="ㄹ 도움")
    await client.change_presence(activity=activity)


# Message Functions


async def rebot_ping(
    args: list[str], ctx: str, is_admin=False
) -> list[str | discord.Embed | discord.File]:
    return [f"퐁! {round(client.latency * 1000)}ms", None, None]


async def rebot_help(
    args: list[str], ctx: str, is_admin=False
) -> list[str | discord.Embed | discord.File]:
    embed = (
        discord.Embed(
            title="REBOT Help",
            color=MAIN_COLOR,
            description="모든 명령은 ㄹ [명령어] 형식입니다.",
        )
        .add_field(name="도움", value="이 도움말을 출력합니다.", inline=False)
        .add_field(name="핑", value="응답시간을 확인합니다.", inline=False)
        .add_field(
            name="급식 [학교명] *[YYYYMMDD]*",
            value="입력한 학교의 급식을 확인합니다. 날짜가 입력되지 않으면 오늘의 급식을 출력합니다.",
            inline=False,
        )
        .add_field(
            name="REEBOT Gemini",
            value="Google Gemini API를 호출합니다.\n사용법: ㄹ [질문]",
            inline=False,
        )
        .add_field(name="초기화", value="REEBOT Gemini와의 대화 내역을 삭제합니다.")
    )
    return [None, embed, None]


async def rebot_foods(
    args: list[str], ctx: str, is_admin=False
) -> list[str | discord.Embed | discord.File]:
    # url = "https://school.cbe.go.kr/daewon-h/M01061701/list?ymd="+args[0]
    # try:
    #     response = requests.get(url)
    #     response.raise_for_status()
    # except requests.exceptions.RequestException as e:
    #     embed = discord.Embed(
    #         title="급식",
    #         description="급식 정보를 가져오는데 실패했습니다.",
    #         color=MAIN_COLOR,
    #     )
    #     return [None, embed, None]
    # else:
    #     soup = bs(response.text, "html.parser")
    #     times = soup.select("li.tch-lnc-wrap > dl > dt")
    #     menus = soup.select("li.tch-lnc-wrap > dl > dd > ul")
    #     menus_list = []
    #     times_list = []
    #     for i in times:
    #         times_list.append(i.get_text())
    #     for i in menus:
    #         menus_list.append(
    #             list(
    #                 map(
    #                     lambda x: re.sub(r"\(.*?\)", "", x.get_text()).strip("\r*+ "),
    #                     i.select("li"),
    #                 )
    #             )
    #         )
    #     embed = discord.Embed(
    #         title="급식", description="급식 정보입니다.", color=MAIN_COLOR
    #     )
    #     for i in range(len(times_list)):
    #         embed.add_field(
    #             name=times_list[i], value="\n".join(menus_list[i]), inline=False
    #         )
    #     return [None, embed, None]
    # GET SCHOOL CODE
    try:
        if len(args) == 0:
            embed = discord.Embed(title="학교명을 입력해주세요!", color=WARN_COLOR)
            return [None, embed, None]
        if len(args) == 1:
            args.append(datetime.now().strftime("%Y%m%d"))
        url = "https://open.neis.go.kr/hub/schoolInfo"
        params = {"KEY": NEIS_TOKEN, "Type": "json", "SCHUL_NM": args[0]}
        response = requests.get(url, params=params)
        data = response.json()["schoolInfo"][1]["row"]
        for i in data:
            if i["SCHUL_NM"] == args[0]:
                data = i
                break
        else:
            data = data[0]

        # GET MEAL
        url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
        params = {
            "KEY": NEIS_TOKEN,
            "Type": "json",
            "ATPT_OFCDC_SC_CODE": data["ATPT_OFCDC_SC_CODE"],
            "SD_SCHUL_CODE": data["SD_SCHUL_CODE"],
            "MLSV_YMD": args[1],
        }
        response = requests.get(url, params=params)
        data = response.json()["mealServiceDietInfo"][1]["row"]
        school_name = data[0]["SCHUL_NM"]
        menu_times = [i["MMEAL_SC_NM"] for i in data]
        menu_list = list(
            map(
                lambda x: re.sub(r"\(.*?\)|\*|\+|\#", "", x["DDISH_NM"]).split("<br/>"),
                data,
            )
        )
        menu_list = [
            list(map(lambda x: x.strip(), menu_list[i])) for i in range(len(menu_times))
        ]

        embed = discord.Embed(
            title="REBOT 급식",
            color=MAIN_COLOR,
            description=f"{school_name}의 급식이에요!",
        )
        for i in range(len(menu_list)):
            embed.add_field(
                name=menu_times[i], value="\n".join(menu_list[i]), inline=False
            )

        return [None, embed, None]
    except Exception as e:
        embed = discord.Embed(title="급식정보를 확인할수 없습니다.", color=WARN_COLOR)
        return [None, embed, None]


async def rebot_eval(
    args: list[str], ctx: str, is_admin=False
) -> list[str | discord.Embed | discord.File]:
    global all
    if is_admin:
        try:
            ctx = ctx[5:]
            await signal(ctx)
            return [f"```{eval(ctx)}```", None, None]
        except Exception as e:
            return ["```" + str(e) + "```", None, None]
    else:
        embed = discord.Embed(
            title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR
        )
        return [None, embed, None]


async def rebot_gemini_prompt(
    args: list[str], ctx: str, is_admin=False
) -> list[str | discord.Embed | discord.File]:
    if is_admin:
        file_to_send = discord.File("./prompts/system_instruction.txt")
        return [None, None, file_to_send]
    else:
        embed = discord.Embed(
            title="REBOT eval", description="권한이 없습니다.", color=WARN_COLOR
        )
        return [None, embed, None]


gemini_queue = {}


async def gemini_queue_call(message: discord.Message):
    if len(gemini_queue[message.guild.id]) != 0:
        gemini_call(gemini_queue[message.guild.id].pop(0))


async def gemini_call(message: discord.Message):
    global gemini_queue, model
    if gemini_queue.get(message.guild.id) == None:
        gemini_queue[message.guild.id] = gemini_queue[message.guild.id] = []
    # try:
    context = message.content[2:]
    if context == "초기화":
        chat_session[message.guild.id] = None
        embed = discord.Embed(
            title="REBOT Gemini", description="초기화 성공!", color=MAIN_COLOR
        )
        await message.channel.send(embed=embed)
        return 0
    if (
        context.startswith("pro ")
        and model.model_name == "models/gemini-1.5-flash"
        and message.author.id in ADMIN_ID
    ):
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
    elif not context.startswith("pro ") and model.model_name == "models/gemini-1.5-pro":
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
        context = message.content[5:]

    if len(gemini_queue[message.guild.id]):

        geminimsg = await message.channel.send("<a:loading:1264015095223287878>")

        if chat_session.get(message.guild.id) == None:
            chat_session[message.guild.id] = model.start_chat(history=[])

        try:
            file_to_send = []
            for i in range(len(message.attachments)):
                filename = f"{message.author.id}-{i}"
                await message.attachments[i].save(filename)
                with PIL.Image.open(filename) as img:
                    file_to_send.append(img.copy())
                os.remove(filename)
            response = chat_session[message.guild.id].send_message(
                [
                    f"날짜 및 시간: {datetime.now()}, 사용자 닉네임: {message.author.display_name}, context: {context}"
                ]
                + file_to_send,
                stream=True,
            )

            responses = ""
            for chunk in response:
                responses += chunk.text
                responses = replace_emoji(responses)
            await discord.Message.edit(self=geminimsg, content=responses)
        except genai.types.BlockedPromptException as e:
            await geminimsg.delete()
            embed = discord.Embed(title="BLOCKED", color=WARN_COLOR).add_field(
                name="세부정보", value=e
            )
            await message.channel.send(embed=embed)
    else:
        gemini_queue[message.guild.id].append(message)

    # if response.text.startswith("/search "):
    #     await discord.Message.edit(self=geminimsg, content="<a:loading:1264015095223287878> Google 검색중....")
    #     search_query = response.text[8:]
    #     search_response = google_search(search_query)
    #     response = chat_session[message.guild.id].send_message("다음 배열중 신뢰성 높은 결과 3개의 인덱스를 출력하십시오. 오직 숫자만 출력하십시오. (예시: 123). 결과를 제공합니다. return: "+str(search_response[0]))
    #     links_index=list(response.text.strip())
    #     await signal(str(links_index))
    #     text_to_send=""
    #     geminimsg = await message.channel.send("<a:loading:1264015095223287878>")
    #     for i in links_index:
    #         text_to_send+=i+" 내용: "+ await web_parse(search_response[1][int(i)])+"\n"
    #     response = chat_session[message.guild.id].send_message("다음 결과를 바탕으로 질문에 대한 답을 제공하시오. return: "+text_to_send)
    #     responses = ""
    #     for chunk in response:
    #         responses += chunk.text
    #         responses = replace_emoji(responses)
    #         await discord.Message.edit(self=geminimsg, content=responses)

    await signal(re.sub(r"`", "\\`", response.text))
    # except Exception as e:
    #     embed = discord.Embed(
    #         title="REBOT Gemini", description=f"오류 발생 {e}", color=WARN_COLOR
    #     )
    #     await message.channel.send(embed=embed)
    #     print(e)


commands_list = {
    "핑": rebot_ping,
    "급식": rebot_foods,
    "eval": rebot_eval,
    "프롬프트": rebot_gemini_prompt,
    "도움": rebot_help,
}

# Client


@client.slash_command(name="핑", description="반응 지연시간을 측정합니다")
async def ping(ctx):
    if ctx.author.id in ADMIN_ID:
        to_send = f"{ctx.author} [ADMIN] : /핑"
        is_admin = True
        await signal(to_send)
    else:
        await signal(f"{ctx.author} : /핑")
        is_admin = False
    content, embed, file = await commands_list["핑"](None, None, is_admin=is_admin)
    await ctx.respond(content)


@client.listen()
async def on_message(message: discord.Message):
    if not message.content.startswith("ㄹ "):
        return
    if message.author.id in ADMIN_ID:
        to_send = f"{message.author} [ADMIN] : {message.content[2:]}"
        is_admin = True
        await signal(to_send)
    else:
        await signal(f"{message.author} : {message.content[2:]}")
        is_admin = False

    args = message.content[2:].split()
    if args[0] in commands_list:
        content, embed, file = await commands_list[args[0]](
            args[1:], message.content[2:], is_admin=is_admin
        )
        await message.channel.send(content, embed=embed, file=file)
    else:
        await gemini_call(message)


client.run(BOT_TOKEN)
