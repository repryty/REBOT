FROM python:3

WORKDIR /usr/src/app

RUN python3 -m pip install py-cord
RUN python3 -m pip install beautifulsoup4
RUN python3 -m pip install requests


COPY . .

CMD ["python3", "./main.py"]
