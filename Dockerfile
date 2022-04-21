FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update -qq \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    wget \
    gcc \
    git \
    ca-certificates \
    vim \
    net-tools \
    && apt-get clean

# PostgreSQL and Python dependencies
RUN true \
    && apt-get -y update -qq \
    && apt-get -y install \
    locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && apt-get -y install \
    -o APT::Install-Recommends="false" \
    -o APT::Install-Suggests="false" \
    build-essential \
    postgresql-contrib \
    &&  apt-get install -y python3-dev python3-pip libpq-dev \
    &&  pip install psycopg2

# Copy all files into the Docker container
WORKDIR /opt/data
COPY src/ /opt/data
