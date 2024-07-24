import asyncio
import multiprocessing as mp
from workers import gemini
import pickle
from typing import Callable
import zlib
import google.generativeai as genai


class MessageQueueRespnose:
    status_code: int
    data: str
    history: list[genai.protos.Content]

    def __init__(self, status_code, data, history) -> None:
        self.status_code = status_code
        self.data = data
        self.history = history


def mq_push(
    callback: Callable[[MessageQueueRespnose]],
    msg: str,
    sender: int,
    attachments: list[str],
    nickname: str,
    history: list[genai.types.ContentDict],
):
    def child():
        resp_raw: bytes = gemini.call(msg, sender, attachments, nickname, history)
        response: tuple[str, list[genai.protos.Content]] = pickle.loads(
            zlib.decompress(resp_raw)
        )
        callback(
            MessageQueueRespnose(
                1 if response[0] == "" else 0, response[0], response[1]
            )
        )

    mp.Process(target=child).start()


def run_async(callback):
    def inner(func):
        def wrapper(*args, **kwargs):
            def __exec():
                out = func(*args, **kwargs)
                callback(out)
                return out

            return asyncio.get_event_loop().run_in_executor(None, __exec)

        return wrapper

    return inner
