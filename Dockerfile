FROM ubuntu:18.04

RUN apt-get -y update && apt-get install -y python-pip python-dev build-essential tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

RUN mkdir -p /opt/starsky

WORKDIR /opt/starsky

COPY app/requirements.txt /opt/starsky/

RUN pip install Cython

RUN pip install -r requirements.txt

COPY app /opt/starsky
