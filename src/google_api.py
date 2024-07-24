from datetime import datetime
import re
import discord
import requests
import google.generativeai as genai
import config
from config import MAIN_COLOR, WARN_COLOR
import utils


def google_search(ctx: str) -> list:
    URL = "https://www.googleapis.com/customsearch/v1"
    params = {"key": config.GOOGLE_TOKEN, "cx": "12e5fcf523c684260", "q": ctx}
    response = requests.get(URL, params)
    items = [i["title"] for i in response.json()["items"]]
    links = [i["link"] for i in response.json()["items"]]
    return [items, links]


chat_session: dict[int, list[genai.types.ContentDict]] = dict()


async def gemini_call(message: discord.Message):
    global gemini_queue, model
    # try:
    context = message.content[2:]
    guild: discord.Guild = message.guild  # type: ignore
    if context == "초기화":
        chat_session[guild.id] = []
        embed = discord.Embed(
            title="REBOT Gemini", description="초기화 성공!", color=MAIN_COLOR
        )
        await message.channel.send(embed=embed)
        return

    geminimsg = await message.channel.send("<a:loading:1264015095223287878>")

    async def callback(response: utils.MessageQueueRespnose):
        if response.status_code != 0:
            # failure
            await geminimsg.delete()
            embed = discord.Embed(title="BLOCKED", color=config.WARN_COLOR).add_field(
                name="세부정보", value=response.data
            )
            await message.channel.send(embed=embed)

            # merge history to main
            chat_session[guild.id] = [
                {"role": i.role, "parts": list(i.parts)} for i in response.history
            ]
        else:
            # succeed
            await discord.Message.edit(self=geminimsg, content=response.data)

    # enqueue
    utils.mq_push(
        callback,
        msg=message.content,
        sender=message.author.id,
        attachments=[i.proxy_url for i in message.attachments],
        nickname=message.author.display_name,
        history=chat_session.get(guild.id, []),
    )
