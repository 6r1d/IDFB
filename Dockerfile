FROM python:3.11-slim

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install nano

RUN mkdir /opt/bot
WORKDIR /opt/bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .

RUN useradd -ms /bin/bash bot && \
    chown bot:bot /opt/bot -R && \
    chown root:root *.py && \
    chmod +x bot.py

USER bot

EXPOSE 8080

ENV PYTHONUNBUFFERED 1

HEALTHCHECK CMD python /opt/bot/healthcheck.py || exit 1

CMD ["/opt/bot/bot.py", "--addr", "0.0.0.0", "--port", "8080", "--rotation_path", "./rotation", "--config", "./config.json", "--telegram_group_id", "/run/secrets/telegram_group_id.txt", "--telegram_token", "/run/secrets/telegram_token.txt", "--github_token", "/run/secrets/github_token.txt"]
