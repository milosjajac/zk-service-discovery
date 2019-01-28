FROM ubuntu:16.04

RUN apt update -y && apt install -y python3-pip python3-dev netcat-openbsd

COPY . /app

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD python3 app.py