#FROM ubuntu:20.04 AS base
FROM docker.io/node:18.20.7-bullseye AS base

ARG LOADDIR="/load-agent"

## Using requirements from https://aries.js.org/guides/getting-started/installation/nodejs/linux

# Setup NodeJS environment for AFJ

ENV TZ=America/Denver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y && apt-get install -y curl gcc g++ make git libssl-dev pkg-config

#RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
#RUN apt-get update -y && apt-get install -y nodejs

#RUN npm install --global yarn

RUN yarn global add ts-node typescript

RUN apt-get install -y libsodium-dev libzmq3-dev

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rust.sh && sh -- rust.sh -y

# Setup Locust

RUN apt-get install -y python3-pip

RUN pip3 install locust==2.14.2

FROM base AS dev

# Setup Dev environment
RUN apt-get install -y tmux htop

# Include global arg in this stage of the build
ARG LOADDIR
# Set working directory to function root directory
WORKDIR ${LOADDIR}

FROM base AS release

# Include global arg in this stage of the build
ARG LOADDIR
# Set working directory to function root directory
WORKDIR ${LOADDIR}

ADD ./load-agent load-agent

WORKDIR ${LOADDIR}/load-agent

RUN yarn install

CMD "locust"
