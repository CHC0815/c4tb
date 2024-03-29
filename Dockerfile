FROM python:3.12-slim AS bot

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

ENV BOT_TOKEN ${BOT_TOKEN}

ADD main.py .
ADD requirements.txt .
ADD bot bot
ADD agents agents

RUN pip3 install -r requirements.txt

CMD python3 main.py;
