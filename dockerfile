FROM python:3

WORKDIR /usr/src/app

RUN python3 -m pip install --progress-bar off py-cord beautifulsoup4 requests

copy token.txt ./
COPY . .

CMD ["python3", "./main.py"]
