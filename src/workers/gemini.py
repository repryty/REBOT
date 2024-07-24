from datetime import datetime
import pickle
import zlib

import requests
import config
import google.generativeai as genai

genai.configure(api_key=config.GEMINI_TOKEN)
flashmodel = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=config.GENERATION_CONFIG,
    system_instruction=config.system_instruction,
    safety_settings=config.SAFETY,
)
promodel = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=config.GENERATION_CONFIG,
    system_instruction=config.system_instruction,
    safety_settings=config.SAFETY,
)
model = flashmodel


def download_attatchment(target: str) -> bytes:
    return requests.get(target).content


def replace_emoji(inp: str) -> str:
    for i in config.EMOJI:
        inp = inp.replace(i, config.EMOJI[i])
    # inp = re.sub(r'([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF])', "", inp)
    return inp


def call(
    msg: str,
    sender: int,
    attachments: list[str],
    nickname: str,
    history: list[genai.types.ContentDict],
) -> bytes:

    global model
    if (
        msg[2:].startswith("pro ")
        and model.model_name == "models/gemini-1.5-flash"
        and sender in config.ADMIN_ID
    ):
        model = promodel
        context = msg[2:]
    elif not msg[2:].startswith("pro ") and model.model_name == "models/gemini-1.5-pro":
        model = flashmodel
        context = msg[5:]
    else:
        context = msg[2:]

    session = model.start_chat(history=history)
    try:
        body: list[object] = [
            f"날짜 및 시간: {datetime.now()}, 사용자 닉네임: {nickname}, context: {context}"
        ]
        for i in attachments:
            body.append(download_attatchment(i))

        response = session.send_message(body, stream=True)

        responses = ""
        for chunk in response:
            responses += chunk.text

        return zlib.compress(pickle.dumps((responses, session.history)))
    except genai.types.BlockedPromptException as e:
        return zlib.compress(pickle.dumps(("", [])))
