"""
This module is responsible for creating and managing a Telegram bot.
It also contains the related utility functions.

Classes:
    - TriageTelegramBot: Telegram bot class for the Triage bot.
"""

import asyncio
from json import dumps, loads
from logging import error
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
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

    def __init__(self, token, config, github_sender):
        self.running = True
        self.router = Router()
        self.dispatcher = Dispatcher()
        self.bot = Bot(token, parse_mode='HTML')
        self.dispatcher.include_router(self.router)
        self.dispatcher.shutdown.register(self.stop)
        self.dispatcher.callback_query.register(self.process_feedback_button_click)
        self.telegram_group_id = config.get('telegram_group_id')
        self.github_sender = github_sender
        self.config = config
        # Register commands
        self.register_commands()

    def stop(self):
        """
        Makes the periodic check function stop.
        Required for a normal shutdown cycle.
        """
        self.running = False

    # Commands
    def register_commands(self):
        """
        Registers multiple bot commands to the aiogram router.

        The following commands are registered:
        - register_group: sets the Telegram group for sending the messages.
        - change_rotation_interval: changes an interval to check for rotated feedback records.
        - change_repository: changes a GitHub issue repository.
        - change_triage_threshold: changes the minimal triage votes

        Note: This method should be called during the initialization phase of the bot
        to ensure all commands are registered before the bot starts processing messages.
        """
        self.router.message.register(
            self.command_register_group,
            Command(commands=['register_group'])
        )
        self.router.message.register(
            self.command_change_rotation_interval,
            Command(commands=['change_rotation_interval'])
        )
        self.router.message.register(
            self.command_change_repository,
            Command(commands=['change_repository'])
        )
        self.router.message.register(
            self.command_change_triage_threshold,
            Command(commands=['change_triage_threshold'])
        )

    async def command_register_group(
        self,
        message: Message,
        _
    ) -> None:
        """
        This handler registers the group with `/register_group` command

        Args:
            message (Message): an aiogram message instance
        """
        self.config.set('telegram_group_id', message.chat.id)
        self.config.save()
        await message.answer(
            f"Group is registered as default: <code>{message.chat.id}</code>"
        )

    async def command_change_rotation_interval(
        self,
        message: Message,
        command: CommandObject
    ) -> None:
        """
        This handler changes the rotation interval config value,
        reacting on the `/change_rotation_interval` command

        Args:
            message (Message): an aiogram message instance
        """
        response = 'Interval changed'
        try:
            interval = int(command.args, 10)
            self.config.set('feedback_rotation_interval', interval)
            self.config.save()
        except ValueError:
            response = f'Invalid interval format: "{command.args}"'
        await message.answer(response)

    async def command_change_repository(
        self,
        message: Message,
        command: CommandObject
    ) -> None:
        """
        This handler changes the default GitHub repository reacting on
        `/change_repository` command

        Args:
            message (Message): an aiogram message instance
        """
        try:
            github_str = 'https://github.com/'
            github_repository: str = command.args.strip()
            if github_repository.startswith(github_str):
                github_repository = github_repository.replace(github_str, '')
            response: str = 'GitHub repository changed'
            if '/' in command.args:
                self.config.set('github_repository', command.args)
                self.config.save()
            else:
                response = f'Invalid repository format: "{command.args}"'
            await message.answer(response)
        except IOError as e:
            error(f"Error changing GitHub repository: {e}")
            await message.answer(
                "An error occurred while changing the repository."
            )

    async def command_change_triage_threshold(
        self,
        message: Message,
        command: CommandObject
    ) -> None:
        """
        This handler changes the triage vote threshold config option,
        reacting on a `/change_triage_threshold` command

        Args:
            message (Message): an aiogram message instance
        """
        response: str = 'Triage vote threshold changed'
        try:
            min_votes: int = int(command.args, 10)
            self.config.set('triage_threshold', min_votes)
            self.config.save()
        except ValueError:
            response = f'Invalid vote count format: "{command.args}"'
        await message.answer(response)

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
                # This part can be ignored safely.
                pass
        # Create a new issue asynchronously (using a thread)
        if vote_count >= self.config.get('triage_threshold'):
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
