FROM python:3

WORKDIR /usr/src/app

RUN python3 -m pip install --progress-bar off py-cord beautifulsoup4 requests


COPY . .

CMD ["python3", "./main.py"]
