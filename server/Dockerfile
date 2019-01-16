FROM python:3.7-alpine

WORKDIR /server

COPY requirements.txt /server/requirements.txt

RUN apk add python-dev build-base gcc && \
pip install --trusted-host pypi.python.org -r requirements.txt && \
apk del python-dev build-base gcc

COPY . /server/

EXPOSE 80
EXPOSE 443

CMD python server.py
