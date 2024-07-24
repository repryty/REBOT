from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import discord
import os

LOADING = "<a:loading:1264015095223287878>"
GENERATION_CONFIG: genai.types.GenerationConfigDict = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}  # type: ignore

SAFETY = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

MAIN_COLOR = discord.Colour.from_rgb(34, 75, 176)
WARN_COLOR = discord.Colour.from_rgb(181, 0, 0)

BOT_TOKEN = os.getenv("REBOT_DISCORD_TOKEN")
GEMINI_TOKEN = os.getenv("REBOT_GEMINI_TOKEN")
NEIS_TOKEN = os.getenv("REBOT_NEIS_TOKEN")
GOOGLE_TOKEN = os.getenv("REBOT_GOOGLE_TOKEN")

with open("prompts/system_instruction.txt", "r", encoding="utf-8") as f:
    system_instruction = f.read()

ADMIN_ID = [784412272805412895, 742067560144437269]

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
