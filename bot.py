#!/usr/bin/env python

"""
Triage bot for user feedback handling.

This bot serves as a bridge between user feedback and the development team.
It transfers user feedback to a Telegram channel for triage,
and then transfers the feedback voted to be useful to GitHub.
"""

import asyncio
from logging import basicConfig as loggingConfig, INFO
from pathlib import Path
from argparse import Namespace
from arguments import get_arguments, ensure_tokens
from github_issue import GitHubSender
from rotation import rotate
from webserver import TriageWebServer
from telegram import TriageTelegramBot
from config import Config

async def main():
    """
    Enable logging, configure the Telegram bot,
    configure the server, start both.
    """
    # Parse the command-line arguments
    input_args: Namespace = get_arguments()
    # Load the tokens from the environment or secrets
    telegram_token, github_token = ensure_tokens(
        input_args, ['telegram_token', 'github_token']
    )
    # Load config
    config = Config(input_args.config)    
    # Configure logging
    loggingConfig(level=INFO)
    # Configure the rotation
    rotation_path = Path(input_args.rotation_path).absolute()
    # Configure the GitHub sender
    github_sender = GitHubSender(
        github_token,
        config.get('github_repository')
    )
    # Configure the Telegram bot
    telegram_bot = TriageTelegramBot(
        token=telegram_token,
        github_sender=github_sender,
        config=config
    )
    telegram_bot_runner = telegram_bot.runner()
    # Configure server
    ws_instance = TriageWebServer(rotation_path)
    http_server = asyncio.create_task(ws_instance.start_http_server(
        bot=telegram_bot,
        address=input_args.address,
        port=input_args.port
    ))
    # Set up file rotation
    rotation_instance = asyncio.create_task(
        rotate(
            telegram_bot,
            rotation_path,
            config.get('feedback_rotation_interval')
        )
    )
    # Gather all AsyncIO runners
    return await asyncio.gather(telegram_bot_runner, http_server, rotation_instance)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    runners = []
    try:
        _, webserver, __ = asyncio.run(main())
        runners.append(webserver.runner)
    finally:
        for runner in runners:
            loop.run_until_complete(runner.cleanup())
