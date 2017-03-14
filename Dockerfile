FROM ubuntu
RUN apt-get -y update
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get -q -y install libleptonica-dev
RUN apt-get -q -y install libtesseract3 libtesseract-dev
RUN apt-get install -q -y tesseract-ocr-eng
COPY app /opt/starsky
WORKDIR /opt/starsky
RUN pip install Cython
RUN pip install -r requirements.txt
