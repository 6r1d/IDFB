FROM python:3.11-slim

ENV  USER=bot
ENV  UID=1000
ENV  GID=1000
ENV  CONFIG_PATH=/opt/bot/
USER root

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install nano

RUN mkdir /opt/bot
WORKDIR /opt/bot

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
     "$USER" && \
     mkdir -p $CONFIG_PATH && \
     chown $USER:$USER -R $CONFIG_PATH

RUN chown bot:bot /opt/bot -R && \
    chown root:root *.py && \
    chmod +x bot.py

USER bot

EXPOSE 8080

ENV PYTHONUNBUFFERED 1

HEALTHCHECK CMD python /opt/bot/healthcheck.py || exit 1

CMD ["/opt/bot/bot.py", "--addr", "0.0.0.0", "--port", "8080", "--rotation_path", "./rotation", "--config", "./config.json"]
