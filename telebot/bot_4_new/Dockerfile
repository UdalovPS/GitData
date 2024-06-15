FROM python:3.11

# create workdir
RUN mkdir /src

# set workdir
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN dpkg --add-architecture i386 && \
        apt-get update && \
        apt-get install -y wine wine32

# copy all files
COPY . .



