FROM python:3.12

WORKDIR /opt/app

ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt \
     && apt update\
     && apt install netcat-traditional

RUN apt-get update && apt-get install -y gettext

COPY . .

EXPOSE 8000

RUN ["chmod", "+x", "/opt/app/run_uwsgi.sh"]

CMD /opt/app/run_uwsgi.sh
