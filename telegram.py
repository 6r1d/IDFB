"""
This module is responsible for creating and managing a Telegram bot.
It also contains the related utility functions.

Classes:
    - TriageTelegramBot: Telegram bot class for the Triage bot.
"""

import asyncio
from json import dumps
from json import loads
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.callback_query import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from hash import title_id_generator

async def generate_keyboard(cnt=0) -> InlineKeyboardBuilder:
    """
    Generate a message keyboard for a feedback message.

    This function creates a keyboard with a single button, used to vote for a new issue.

    Args:
        cnt (int): The count to display on the button label, indicating the number of issues.

    Returns:
        aiogram.utils.keyboard.InlineKeyboardBuilder:
            An InlineKeyboardBuilder object containing the generated keyboard.
    """
    if cnt == 0:
        text = 'New issue'
    else:
        text = f'New issue ({cnt})'
    callback_data = dumps(
        {'mode': 'triage', 'voters': []},
        ensure_ascii=False
    )
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=text,
        callback_data=callback_data
    ))
    return builder

async def render_feedback_msg(data: dict) -> str:
    """
    Render a feedback message to be sent in a chat.

    Args:
        req_data (dict): A dictionary containing request data,
                         including request text, contact information,
                         and type of feedback like a bug or suggestion.

    Returns:
        str: A formatted feedback message to send in the chat.
    """
    kind_icon = '📝'
    if data.get('kind') == 'bug':
        kind_icon = '🐞'
    if data.get('kind') == 'suggestion':
        kind_icon = '🤔'
    text = f'{kind_icon} <b>Feedback</b>\n\n' + \
           f'<b>User</b>: <code>{data.get("contact")}</code>\n' + \
           f'<b>Page</b>: <code>{data.get("location")}</code>\n\n' + \
           data.get('feedback')
    return text

class TriageTelegramBot:
    """
    Telegram part of the bot.

    Example usage:
        bot = TriageTelegramBot("YOUR_BOT_TOKEN", "YOUR_TELEGRAM_GROUP_ID", 5, github_sender)
        await asyncio.gather(bot.runner())
    """

    def __init__(self, token, telegram_group_id,
                 config, github_sender):
        self.running = True
        self.router = Router()
        self.dispatcher = Dispatcher()
        self.bot = Bot(token, parse_mode='HTML')
        self.dispatcher.include_router(self.router)
        self.dispatcher.shutdown.register(self.stop)
        self.dispatcher.callback_query.register(self.process_feedback_button_click)
        self.telegram_group_id = telegram_group_id
        self.github_sender = github_sender
        self.config = config
        # Amount of people needed for triage
        self.triage_threshold = config.get('triage_threshold')
        # Register commands
        self.router.message.register(
            self.command_register_group,
            Command(commands=["register_group"])
        )

    def stop(self):
        """
        Makes the periodic check function stop.
        Required for a normal shutdown cycle.
        """
        self.running = False

    # Commands
    async def command_register_group(self, message: Message) -> None:
        """
        This handler registers the group with `/register_group` command

        Args:
            message (Message): an aiogram message instance
        """
        self.config.set('telegram_group_id', message.chat.id)
        self.config.save()
        await message.answer(f"Group is registered as default: <code>{message.chat.id}</code>")

    # Generic feedback processing
    async def process_feedback_button_click(self, cbq: CallbackQuery):
        """
        Processes the button reaction,
        updates the votes,
        sends out a GitHub issue with enough votes and edits a message.

        Args:
            cbq (CallbackQuery)
        """
        username = cbq.from_user.username
        metadata = loads(cbq.data)
        vote_count = len(metadata['voters'])
        if username not in metadata['voters']:
            metadata['voters'].append(username)
            vote_count += 1
            builder = await generate_keyboard(len(metadata['voters']))
            try:
                await cbq.message.edit_text(
                    cbq.message.text,
                    reply_markup=builder.as_markup()
                )
                await cbq.answer("Thank you for your vote!")
            except TelegramBadRequest:
                # Telegram API tends to throw it on button edits
                # as the text remains the same.
                pass
        # Create a new issue asynchronously (using a thread)
        if vote_count >= self.triage_threshold:
            await self.send_feedback_to_github(cbq.message)

    async def send_feedback_to_github(self, tg_message):
        """
        Sends out a GitHub issue with enough votes and edits a message.

        Args:
            tg_message (aiogram.types.message.Message): a Telegram message instance
        """
        title = title_id_generator()
        issue_coro = asyncio.to_thread(
            self.github_sender.create_issue,
            title,
            tg_message.text
        )
        issue_url = await issue_coro
        await tg_message.edit_text(
            (
                f'New issue available:\n'
                f'<a href="{issue_url}">{title}</a>.'
            )
        )

    async def runner(self) -> None:
        """
        Returns:
            (coroutine): bot coroutine
        """
        await self.dispatcher.start_polling(self.bot)

    async def send_to_telegram_group_id(self, text: str, **kwargs):
        """
        Send a text to the chat with a current telegram_group_id.

        Args:
            text (str): a string to be sent
        """
        return await self.bot.send_message(
            chat_id=self.telegram_group_id,
            text=text,
            **kwargs
        )
