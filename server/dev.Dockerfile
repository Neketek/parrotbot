FROM python:3.7-alpine

WORKDIR /server

COPY requirements.txt /server/requirements.txt

CMD pip install --trusted-host pypi.python.org -r requirements.txt

RUN python server.py
