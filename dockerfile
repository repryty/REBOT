FROM python:3

WORKDIR /usr/src/app
ENV REBOT_DISCORD_TOKEN "undefined" \
    REBOT_GEMINI_TOKEN "undefined"


RUN python3 -m pip install --progress-bar off py-cord beautifulsoup4 requests google-generativeai

COPY . .

CMD ["python3", "./main.py"]
