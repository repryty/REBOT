FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt
RUN python3 -m pip install --progress-bar off -r requirements.txt

COPY token.txt ./
COPY . .

CMD ["python3", "./main.py"]
