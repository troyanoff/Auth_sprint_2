FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && apt update\
    && apt install netcat-traditional

COPY ./src .

COPY run.sh run.sh

EXPOSE 8200

ENTRYPOINT ["sh", "run.sh"]
       