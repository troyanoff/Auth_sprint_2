FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt
COPY run.sh run.sh

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && apt update\
    && apt install netcat-traditional

COPY ./src .

EXPOSE 8000

ENTRYPOINT ["sh", "run.sh"]
