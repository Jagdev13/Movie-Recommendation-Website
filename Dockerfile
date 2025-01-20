FROM python:3.8.5
ENV PYTHONBUFFERED=1
RUN mkdir -p /usr/app
WORKDIR /usr/app
COPY requirements.txt /usr/app
RUN apt-get update
RUN python3 -m pip install -U pip
RUN pip install -r requirements.txt
COPY . /usr/app