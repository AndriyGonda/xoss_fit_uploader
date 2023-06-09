FROM python:3.10
ENV COMPOSE_HTTP_TIMEOUT 120
COPY . /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

RUN apt update
