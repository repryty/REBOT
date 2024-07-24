from datetime import datetime
import re
from typing import Callable, Coroutine
import discord
import requests
import os

import config

type DiscordCommandResponse = str | discord.Embed | discord.File

MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)
WARN_COLOR = discord.Colour.from_rgb(181, 0, 0)


async def rebot_ping(
    args: list[str], ctx: str, is_admin=False
) -> DiscordCommandResponse:
    return f"퐁! {round(client.latency * 1000)}ms"


async def rebot_help(
    args: list[str], ctx: str, is_admin=False
) -> DiscordCommandResponse:
    return (
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


async def rebot_foods(
    args: list[str], ctx: str, is_admin=False
) -> DiscordCommandResponse:
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
            return discord.Embed(title="학교명을 입력해주세요!", color=WARN_COLOR)
        if len(args) == 1:
            args.append(datetime.now().strftime("%Y%m%d"))

        url = "https://open.neis.go.kr/hub/schoolInfo"
        params = {"KEY": config.NEIS_TOKEN, "Type": "json", "SCHUL_NM": args[0]}
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
            "KEY": config.NEIS_TOKEN,
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

        return embed
    except Exception:
        embed = discord.Embed(title="급식정보를 확인할수 없습니다.", color=WARN_COLOR)
        return embed


async def rebot_gemini_prompt(
    args: list[str], ctx: str, is_admin=False
) -> DiscordCommandResponse:
    if is_admin:
        return discord.File("./prompts/system_instruction.txt")
    else:
        return discord.Embed(
            title="REBOT eval", description="권한이 없습니다.", color=WARN_COLOR
        )


async def rebot_eval(
    args: list[str], ctx: str, is_admin=False
) -> DiscordCommandResponse:
    global all
    if is_admin:
        try:
            ctx = ctx[5:]
            await signal(ctx)
            return f"```{eval(ctx)}```"
        except Exception as e:
            return "```" + str(e) + "```"
    else:
        embed = discord.Embed(
            title="REBOT eval", description="권한이 없습니다.", color=MAIN_COLOR
        )
        return embed


commands_list: dict[
    str,
    Callable[
        [list[str], str, bool],
        Coroutine[object, object, DiscordCommandResponse],
    ],
] = {
    "핑": rebot_ping,
    "급식": rebot_foods,
    "eval": rebot_eval,
    "프롬프트": rebot_gemini_prompt,
    "도움": rebot_help,
}
