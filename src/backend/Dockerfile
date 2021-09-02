# FROM python:3.9.4-slim
# LABEL maintainer "Ian Mungovan <Ian.Mungovan1@gmail.com>"
# RUN apt-get update \
#     && apt-get upgrade -y \
#     && apt-get install -y \
#     && apt-get -y install unixodbc unixodbc-dev apt-utils netcat gunicorn libpq-dev python3-dev gcc libpq-dev build-essential vim \
#     && apt-get autoremove -y \
#     && apt-get clean all
# ENV INSTALL_PATH /usr/mec/static
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# RUN mkdir -p $INSTALL_PATH
# COPY requirements.txt .
# RUN pip install --upgrade pip setuptools wheel
# RUN pip install -v uvloop
# RUN pip install -r requirements.txt
# COPY . .
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
# RUN apk add --no-cache \
#     gcc \
#     python3-dev \
#     libffi-dev \
#     # openssl-dev \
#     cargo \
#     libressl-dev \
#     musl-dev \
#     libffi-dev && \
#     pip install --no-cache-dir cryptography && \
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    && apt-get -y install unixodbc unixodbc-dev apt-utils netcat gunicorn libpq-dev python3-dev gcc libpq-dev build-essential vim \
    && apt-get autoremove -y \
    && apt-get clean all
RUN pip install --upgrade pip setuptools wheel
# WORKDIR /app
COPY requirements.txt .
# COPY pyproject.toml .
# COPY pdm.lock .
RUN pip install -r requirements.txt
# RUN pdm install --prod
# COPY . /app