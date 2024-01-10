FROM python:3.11-slim

ENV  USER=bot
ENV  UID=1000
ENV  GID=1000
USER root

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install nano

ENV  CONFIG_PATH=/opt/bot
RUN  mkdir -p $CONFIG_PATH
WORKDIR $CONFIG_PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .

RUN  set -ex && \
     addgroup -gid $GID $USER && \
     adduser \
     --disabled-password \
     --gecos "" \
     --home /app \
     --ingroup "$USER" \
     --uid "$UID" \
     "$USER"

RUN chown $USER:$USER $CONFIG_PATH -R && \
    chown root:root *.py && \
    chmod +x bot.py

USER $USER

EXPOSE 8080

ENV PYTHONUNBUFFERED 1

HEALTHCHECK CMD python $CONFIG_PATH/healthcheck.py || exit 1

CMD ["/opt/bot/bot.py", "--addr", "0.0.0.0", "--port", "8080", "--rotation_path", "/opt/bot/rotation", "--config", "/opt/bot/config.json"]
