import discord
import io
import contextlib
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
from google.api_core.exceptions import ResourceExhausted
import random

from config import *

type DiscordCommandResponse = str | discord.Embed | discord.File

class Gemini:
    def __init__(self, generation_config: dict) -> None:
        self.queue={}
        self.sessions: dict[ list[genai.GenerativeModel] ]={}
        self.files: dict[ list ] = {}
        self.generation_config=DEFAULT_GENERATION_CONFIG
        self.system_instruction = dict()

    async def push(self, ctx:discord.Message, id: int, msg: discord.Message)->None:
        self.queue[id].append([ctx, msg])

    async def reset(self, id: int, instruction: str = DEFAULT_SYSTEM_INSTRUCTION)->None:
        self.queue[id]=[]
        self.system_instruction[id] = instruction if instruction != DEFAULT_SYSTEM_INSTRUCTION else DEFAULT_SYSTEM_INSTRUCTION
        try: model_name=self.sessions[id].model.model_name
        except: model_name="gemini-1.5-flash"
        self.sessions[id]=genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_instruction[id],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        ).start_chat()

        if self.files.get(id)!=None:
            for i in self.files[id]:
                print(f"deleted {i.name}")
                i.delete()
        self.files[id]=[]

        self.generation_config=DEFAULT_GENERATION_CONFIG

    async def change_model(self, id: int, model: str)->None:
        if self.sessions.get(id)==None:
            await self.reset(id)
        history=self.sessions[id].history
        model = genai.GenerativeModel(
            model_name=model,
            generation_config=self.generation_config,
            system_instruction=self.system_instruction[id],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.sessions[id]=model.start_chat(history=history)

    async def call(self, id: int)->None | list[discord.Embed | discord.Message]:
        try:
            queue=self.queue[id].pop(0)
            msg: discord.Message=queue[1]
            ctx: discord.Message=queue[0]
            content=[f"날짜 및 시간: {datetime.now()}, 사용자 닉네임: {ctx.author.display_name}, context: {ctx.content[2:]}"]
            for i in ctx.attachments:
                filename=f"{ctx.guild.id}-{ctx.attachments.index(i)}.{i.filename.split(".")[-1]}"
                await i.save(filename)
                file=genai.upload_file(filename)
                self.files[id].append(file)
                content.append(file)
                os.remove(filename)
                print(1)
            # print(content)
            response = self.sessions[id].send_message(content, stream=True)
            responses = ""
            for chunk in response:
                responses += make_emoji(chunk.text)
                for_return=""
                if len(responses)>1900: 
                    await msg.edit(responses[:1900])
                    for_return+=responses[:1900]
                    responses=responses[1900:]
                    msg = await msg.channel.send(responses)
                await msg.edit(responses)

            return [for_return+responses, None]
        except genai.types.BlockedPromptException as e:
            embed=discord.Embed(
                title="BLOCKED",
                color=WARN_COLOR
            ).add_field(name="세부정보", value=e)
            return [embed, msg]
        except ResourceExhausted:
            embed=discord.Embed(
                title="REBOT Gemini",
                color=WARN_COLOR
            ).add_field(name="Gemini API 사용량 제한 초과", value="Gemini 1.5 Flash를 사용하거나, 잠시 기다려주세요.")
            return [embed, msg]
        
    async def set_temp(self, temp: int)->None:
        self.generation_config["TEMPERATURE"] = temp
        
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
            "도움": self.help,
            "프롬프트": self.gemini_change_instruction,
            "빈칸": self.make_test,
            "텍스트추출": self.image_to_text,
            "명령어": self.get_commands_list,
            "temp": self.set_temp,
            "d": self.dice
        }

    async def get_commands_list(self)-> DiscordCommandResponse:
        return ", ".join(self.commands_list.keys())

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

    async def dice(self):
        return f"🎲! {random.randint(1, self.args[0])}!"
    
    async def gemini_reset(self) -> DiscordCommandResponse:
        await self.gemini.reset(id=self.message.guild.id)
        embed=discord.Embed(
            title="REBOT Gemini",
            color=MAIN_COLOR
        ).add_field(
            name="초기화 성공!",
            value=self.gemini.sessions[self.message.guild.id].model.model_name
                .replace("models/gemini-1.5-pro-exp-0827", "Gemini 1.5 Pro Experimental 0827")
                .replace("models/gemini-1.5-pro-002", "Gemini 1.5 Pro 002")
                .replace("models/gemini-1.5-flash", "Gemini 1.5 Flash")
                .replace("models/gemini-1.5-flash-exp-0827", "Gemini 1.5 Flash Experimental 0827")
        )
        return embed
        
    async def gemini_change_model(self) -> DiscordCommandResponse:
        print(self.args)
        if self.args[0]=="pro":
            await self.gemini.change_model(self.message.guild.id, "gemini-1.5-pro-002")
            using="Gemini 1.5 Pro 002"
        elif self.args[0]=="flash":
            await self.gemini.change_model(self.message.guild.id, "gemini-1.5-flash")
            using="Gemini 1.5 Flash"
        elif self.args[0]=="flashex":
            await self.gemini.change_model(self.message.guild.id, "gemini-1.5-flash-exp-0827")
            using="Gemini 1.5 Flash Experimental 0827"
        elif self.args[0]=="proex":
            await self.gemini.change_model(self.message.guild.id, "gemini-1.5-pro-exp-0827")
            using="Gemini 1.5 Pro Experimental 0827"
        else:
            try:
                embed=discord.Embed(
                    title="REBOT Gemini",
                    color=MAIN_COLOR
                ).add_field(
                    name="현재 사용중인 모델",
                    value=self.gemini.sessions[self.message.guild.id].model.model_name
                        .replace("models/gemini-1.5-pro-exp-0827", "Gemini 1.5 Pro Experimental 0827")
                        .replace("models/gemini-1.5-pro-002", "Gemini 1.5 Pro 002")
                        .replace("models/gemini-1.5-flash", "Gemini 1.5 Flash")
                        .replace("models/gemini-1.5-flash-exp-0827", "Gemini 1.5 Flash Experimental 0827")
                )
            except:
                embed=discord.Embed(
                    title="REBOT Gemini",
                    color=MAIN_COLOR
                ).add_field(
                    name="현재 사용중인 모델",
                    value="Gemini 1.5 Flash"
                )
            return embed
        embed=discord.Embed(
            title="REBOT Gemini",
            color=MAIN_COLOR
        ).add_field(
            name="모델이 성공적으로 변경되었습니다!",
            value=using
        )
        return embed
    
    async def help(self)->DiscordCommandResponse:
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
            value="REEBOT Gemini와의 대화 내역을 삭제합니다.",
            inline=False
            
        ).add_field(
            name="모델",
            value="리봇의 모델을 pro/flash중 선택합니다.",
            inline=False
        )
        # .add_field(
        #     name="급식 [학교명] *[YYYYMMDD]*",
        #     value="입력한 학교의 급식을 확인합니다. 날짜가 입력되지 않으면 오늘의 급식을 출력합니다.",
        #     inline=False
        # )
        return embed
    
    async def make_test(self)->DiscordCommandResponse:
        self.args.pop()
        probability = int(self.args.pop(0))
        msg = []
        for i in self.args:
            if random.randint(0, 99)<=probability and not ("\n" in i):
                msg.append("_"*round(len(i)*1.5))
            else:
                msg.append(i)
        output = f"```\n{" ".join(msg)}\n```\n```\n{" ".join([re.sub(r"_", r"\_", i) for i in msg])}\n```"
        if len(output)>1998:
            with open(f"{self.message.author.id}.txt", "w") as f:
                f.write(output)
            return discord.File(fp=f"{self.message.author.id}.txt")
        return output

    async def image_to_text(self)->DiscordCommandResponse:
        filename= f"{self.message.author.id}.{self.message.attachments[0].filename.split(".")[-1]}"
        await self.message.attachments[0].save(filename)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-002",
            generation_config = {
                "temperature": 0.0,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            },
            system_instruction="입력된 이미지에서 문자를 추출하시오. 추출한 문자를 적절한 코드 블럭 안에 넣으시오. 만약 문자가 파이썬 코드라면 # 이후의 문자는 추출하지 마시오. 띄어쓰기를 주의해서 작성하시오.",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        file = genai.upload_file(filename)
        response = model.generate_content(["추출할 이미지", file])
        file.delete()
        os.remove(filename)
        return response.text
    

    async def set_temp(self)->DiscordCommandResponse:
        self.args.pop()
        temp = float(self.args.pop(0))
        self.gemini.set_temp(temp)
        return discord.Embed(title="REEBOT Gemini", color=MAIN_COLOR, description=f"성공적으로 temperature가 {temp}로 변경되었습니다!")

    # async def yt_dlp(self)->DiscordCommandResponse:
    #     # os.chdir("utils")
    #     # os.system(f'yt-dlp -S "height:1080" -f "bv*" --no-playlist --ffmpeg-location ffmpeg -o "{self.message.author.id}.%(ext)s" {self.args[0]}')
    #     # filename=""
    #     # for i in os.listdir():
    #     #     if i.startswith(str(self.message.author.id)):
    #     #         filename=i
    #     #         break
    #     # shutil.move(filename, "../files/attachments")
    #     # os.chdir("..")
    #     # return discord.File("files/attachments/"+filename)

    #     os.chdir("utils")
    #     result = subprocess.run(
    #         ['yt-dlp', '-S', 'height:1080', '-f', 'bv*', '--no-playlist', '--get-url', self.args[0]],
    #         capture_output=True,
    #         text=True
    #     )
    #     os.chdir("..")
    #     embed=discord.Embed(
    #         title="YouTube Downloader",
    #         color=MAIN_COLOR
    #     ).add_field(
    #         name="성공!",
    #         value=f"[다운로드]({result.stdout})"
    #     )
    #     return embed
    
    async def gemini_change_instruction(self)->discord.Embed:
        self.args.pop()
        if len(self.message.attachments)==1:
            file=self.message.attachments[0]
            filename=f"{self.message.guild.id}.{file.filename.split(".")[-1]}"
            await file.save(filename)
            with open(filename, "r", encoding="utf-8") as opened_file:
                instruction=opened_file.read()
            await self.gemini.reset(id=self.message.guild.id, instruction=instruction)
            
        elif self.args==[]:
            await self.gemini.reset(id=self.message.guild.id)
        else:
            await self.gemini.reset(id=self.message.guild.id, instruction=' '.join((self.args)))
        embed=discord.Embed(
            title="REBOT Gemini",
            color=MAIN_COLOR
        ).add_field(
            name="프롬프트 변경 성공!",
            value=self.gemini.sessions[self.message.guild.id].model.model_name
                .replace("models/gemini-1.5-pro-exp-0827", "Gemini 1.5 Pro Experimental 0827")
                .replace("models/gemini-1.5-pro", "Gemini 1.5 Pro")
                .replace("models/gemini-1.5-flash", "Gemini 1.5 Flash")
                .replace("models/gemini-1.5-flash-exp-0827", "Gemini 1.5 Flash Experimental 0827")
        )
        return embed