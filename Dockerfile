ARG NODE_VERSION=18.18.2

FROM python:3.9 as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /sinpp

FROM base as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.5.0

RUN pip install "poetry==$POETRY_VERSION"

COPY . /sinpp

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root

# tsc part
ARG NODE_VERSION
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN npm install -g typescript

FROM base as final
ARG NODE_VERSION
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
COPY --from=builder /sinpp/ /sinpp/
COPY --from=builder /root/.nvm/ /root/.nvm/
