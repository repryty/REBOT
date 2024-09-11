import os
import discord
import re

BOT_TOKEN = os.getenv("REBOT_DISCORD_TOKEN")
GEMINI_TOKEN = os.getenv("REBOT_GEMINI_TOKEN")
NEIS_TOKEN = os.getenv("REBOT_NEIS_TOKEN")

ADMIN_ID = [
    784412272805412895, # 리프
    742067560144437269 
    ]
NOTICE_CHANNEL=1261486436771823700
MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)
WARN_COLOR = discord.Colour.from_rgb(181, 0, 0)
EMOJI = {
    r"🚪": "<:me:1144858072624406588>",
    r"⭐": "<:star:1144858244909633619>",
    r"❓": "<a:what:1144859308299923536>",
    r"🚫": "<:no:1144857465566003253>",
    r"🌸": "<:hwal:1144858220263907358>",
    r"😊": "<:happy:1144857824866861056>",
    r"✍🏼": "<:grab:1144857312377446410>",
    r"😔": "<:hing:1144858197551759410>",
    r"🫠": "<:liquid:1144857660836036609>",
    r"😢": "<:sad:1144857284112040026>",
}

generation_config = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

DEFAULT_SYSTEM_INSTRUCTION = open("system_instruction/system_instruction.txt", "r", encoding="utf-8").read()
system_instruction = DEFAULT_SYSTEM_INSTRUCTION

def make_emoji(ctx: str | None)->str:
    if ctx==None: return None
    for key, value in EMOJI.items():
        ctx = re.sub(key, value, ctx)
    return ctx