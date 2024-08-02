import discord
import io
import contextlib
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime

from config import *

type DiscordCommandResponse = str | discord.Embed | discord.File

class Gemini:
    def __init__(self, generation_config: dict, system_instruction: str) -> None:
        self.queue={}
        self.sessions: dict[ genai.GenerativeModel ]={}
        self.flashmodel = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.promodel = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.proexmodel = genai.GenerativeModel(
            model_name="gemini-1.5-pro-exp-0801",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

    async def push(self, ctx:discord.Message, id: int, msg: discord.Message)->None:
        self.queue[id].append([ctx, msg])

    async def reset(self, id: int)->None:
        self.queue[id]=[]
        self.sessions[id]=self.flashmodel.start_chat()

    async def change_model(self, id: int, model: genai.GenerativeModel)->None:
        if self.sessions.get(id)==None:
            await self.reset(id)
        history=self.sessions[id].history
        self.sessions[id]=model.start_chat(history=history)

    async def call(self, id: int)->None | list[discord.Embed | discord.Message]:
        try:
            queue=self.queue[id].pop(0)
            msg: discord.Message=queue[1]
            ctx: discord.Message=queue[0]
            content=[f"날짜 및 시간: {datetime.now()}, 사용자 닉네임: {ctx.author.display_name}, context: {ctx.content}"]
            for i in ctx.attachments:
                filename=f"{ctx.guild.id}-{ctx.attachments.index(i)}.{i.filename.split(".")[-1]}"
                await i.save(filename)
                file=genai.upload_file(filename)
                content.append(file)
                print(1)
            # print(content)
            response = self.sessions[id].send_message(content, stream=True)

            responses = ""
            for chunk in response:
                responses += make_emoji(chunk.text)
                await msg.edit(responses)
            for i in content[1:]:
                genai.delete_file(i.name)
                os.remove(i.display_name)
            return [responses, None]
        except genai.types.BlockedPromptException as e:
            embed=discord.Embed(
                title="BLOCKED",
                color=WARN_COLOR
            ).add_field(name="세부정보", value=e)
            return [embed, msg]
        
class Commands:
    def __init__(self, args: list[str], message: discord.Message, client: discord.Client, gemini=Gemini) -> None:
        self.args = args
        self.message = message
        self.client = client
        self.gemini = gemini

        
        self.commands_list = {
            "핑": self.ping,
            "eval": self.eval,
            "exec": self.exec,
            "초기화": self.gemini_reset,
            "모델": self.gemini_change_model,
            "도움": self.help
        }

    async def ping(self) -> DiscordCommandResponse:
        return f"퐁! {round(self.client.latency * 1000)}ms"

    async def exec(self) -> DiscordCommandResponse:
        if not self.args.pop(): return "권한없음"
        code = ' '.join(self.args)
        str_io = io.StringIO()
        try:
            with contextlib.redirect_stdout(str_io):
                exec(code)
        except Exception as e:
            return f"오류 발생: {e}"
        return f"```{str_io.getvalue()}```".replace("``````", "출력이 없습니다.")

    async def eval(self) -> DiscordCommandResponse:
        # print(self.args)
        if not self.args.pop(): return "권한없음"
        try:
            result = eval(' '.join((self.args)))
            return f"```{result}```"
        except Exception as e:
            return f"오류 발생: {e}"
    
    async def gemini_reset(self) -> DiscordCommandResponse:
        await self.gemini.reset(id=self.message.guild.id)
        embed=discord.Embed(
            title="REBOT Gemini",
            color=MAIN_COLOR
        ).add_field(
            name="초기화 성공!",
            value=""
        )
        return embed
        
    async def gemini_change_model(self) -> DiscordCommandResponse:
        if self.args[0]=="pro":
            await self.gemini.change_model(self.message.guild.id, self.gemini.promodel)
            using="Gemini 1.5 Pro"
        elif self.args[0]=="flash":
            await self.gemini.change_model(self.message.guild.id, self.gemini.flashmodel)
            using="Gemini 1.5 Flash"
        elif self.args[0]=="proex":
            await self.gemini.change_model(self.message.guild.id, self.gemini.proexmodel)
            using="Gemini 1.5 Pro Experience"
        else:
            embed=discord.Embed(
                title="REBOT Gemini",
                color=WARN_COLOR
            ).add_field(
                name="올바른 모델명을 입력해주세요.",
                value="pro / flash"
            )
            return embed
        embed=discord.Embed(
            title="REBOT Gemini",
            color=MAIN_COLOR
        ).add_field(
            name="모델이 성공적으로 변경되었습니다!",
            value="현재 사용중: "+using
        )
        return embed
    
    async def help(self):
        embed=discord.Embed(
            title="REBOT Help",
            color=MAIN_COLOR,
            description="모든 명령은 ㄹ [명령어] 형식입니다."
        ).add_field(
            name="도움",
            value="이 도움말을 출력합니다.",
            inline=False
        ).add_field(
            name="핑",
            value="응답시간을 확인합니다.",
            inline=False
        ).add_field(
            name="REEBOT Gemini",
            value="Google Gemini API를 호출합니다.\n사용법: ㄹ [질문]",
            inline=False
        ).add_field(
            name="초기화",
            value="REEBOT Gemini와의 대화 내역을 삭제합니다."
        ).add_field(
            name="모델",
            value="리봇의 모델을 pro/flash중 선택합니다."
        )
        # .add_field(
        #     name="급식 [학교명] *[YYYYMMDD]*",
        #     value="입력한 학교의 급식을 확인합니다. 날짜가 입력되지 않으면 오늘의 급식을 출력합니다.",
        #     inline=False
        # )
        return embed