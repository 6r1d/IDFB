"""
This module provides functions to manage the rotation of unsent feedback messages
and ensure they are sent to the designated group chat. It includes utilities for
finding and processing JSON files containing feedback data and sending the messages
with a vote button for user interaction.
"""

import asyncio
from json import load
from pathlib import Path
from aiogram.exceptions import AiogramError
from telegram import render_feedback_msg, generate_keyboard

def find_single_file(directory_path, extension):
    """
    Find a single file in the specified directory.

    Args:
        directory_path (str or Path): The path to the directory to search for a JSON file.
        extension (str): File extension, e.g., 'json'

    Returns:
        Path or None: Returns the path to the found file or None if not found.
    """
    directory = Path(directory_path)
    if directory.is_dir():
        for file_path in directory.glob(f'*.{extension}'):
            return file_path
    return None

async def rotate(bot, rotation_path, sleep_interval=1):
    """
    Checks the path to unsent messages and sends them later to ensure they are sent.

    Args:
        bot (TriageTelegramBot): Bot instance.
        rotation_path (pathlib.Path): Path to check.
        sleep_interval (int): Check delay in seconds.
    """
    while bot.running:
        text = None
        rfile = find_single_file(rotation_path, 'json')
        if rfile:
            with open(rfile, 'r', encoding='utf-8') as rfile_inst:
                req_data = load(rfile_inst)
                text = await render_feedback_msg(req_data)
        if text:
            # Add a button to the feedback message
            builder = await generate_keyboard()
            try:
                await bot.send_to_telegram_group_id(
                    text, reply_markup=builder.as_markup()
                )
                rfile.unlink()
            except AiogramError:
                pass
        await asyncio.sleep(sleep_interval)
