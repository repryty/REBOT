FROM python:3

WORKDIR /usr/src/app
ENV REBOT_DISCORD_TOKEN "undefined"
ENV REBOT_GEMINI_TOKEN "undefined"
ENV TZ Asia/Seoul


RUN python3 -m pip install -r requirements.txt

COPY . .

CMD ["python3", "./main.py"]
