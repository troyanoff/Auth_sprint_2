FROM python:3.10

WORKDIR /app_tests

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && apt update\
    && apt install netcat-traditional

COPY ./functional .

COPY create_superuser.py .

COPY truncate_tables.py .

EXPOSE 9001

ENTRYPOINT ["sh", "run_tests.sh"]
       