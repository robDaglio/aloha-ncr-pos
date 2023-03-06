FROM docker.mysck.net/third-party/python:3.10
LABEL project="Aloha NCR/POS Date Corrections Microservice"
LABEL maintainer="saasteam@kitchenbrains.com"
ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/logs
WORKDIR /usr/src/app

RUN /usr/local/bin/python3.10 -m pip install --upgrade pip
RUN rm -rf ~/.cache/pip

COPY . /usr/src/app
RUN /usr/local/bin/python3.10 -m pip install -r requirements.txt
CMD ["/usr/local/bin/python3.10", "/usr/src/app/main.py"]