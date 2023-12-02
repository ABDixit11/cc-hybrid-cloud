ARG PYTHON_VERSION=3.8
FROM --platform=${TARGETPLATFORM:-linux/amd64} ghcr.io/openfaas/of-watchdog:0.9.10 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/amd64} python:${PYTHON_VERSION}-alpine as build

RUN apk update && apk add --no-cache \
    build-base \
    cmake \
    ca-certificates \
    python3-dev \
    py3-pip \
    libx11-dev \
    musl-dev \
    libffi-dev \
    libgcc \
    libstdc++ \
    libxext \
    libxrender \
    libgomp \
    ffmpeg

RUN python -m pip install --upgrade pip

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

RUN apk --no-cache add ${ADDITIONAL_PACKAGE}

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY --chown=app:app index.py           .
COPY --chown=app:app requirements.txt   .
USER root
RUN pip install  -r requirements.txt

# Build the function directory and install any user-specified components
USER app

RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/app/function/
COPY --chown=app:app function/requirements.txt	.
COPY function/encoding .
RUN pip install  --user -r requirements.txt

# install function code
USER root
COPY --chown=app:app function/   .

FROM build as test
ARG TEST_COMMAND=tox
ARG TEST_ENABLED=true
RUN [ "$TEST_ENABLED" = "false" ] && echo "skipping tests" || eval "$TEST_COMMAND"

FROM build as ship
WORKDIR /home/app/

# configure WSGI server and healthcheck
USER app

ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5001"

#HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]