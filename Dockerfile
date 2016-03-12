FROM python:3.5-alpine

MAINTAINER Leon de Jager <ldejager@coretanium.net>

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["python", "-u", "vmsuperhub.py"]