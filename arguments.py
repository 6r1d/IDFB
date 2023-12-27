"""
This module configures the Argparse library to parse command-line arguments
required for the Soramitsu Iroha feedback bot.
"""

from os.path import isdir, isfile
from argparse import ArgumentParser, FileType
from pathlib import Path

def dir_path(dir_path: str) -> Path:
    """
    Ensure that the supplied input is a valid directory path.

    Args:
        dir_path (str): input directory location

    Returns:
        Path: A Path object representing the validated directory path.

    Raises:
        NotADirectoryError: If the dir_path does not exist or is not a directory.
    """
    if not isdir(dir_path):
        raise NotADirectoryError(f'"{dir_path}" is not a valid directory.')
    return Path(dir_path)

def file_path(file_path: str) -> Path:
    """
    Ensure that the supplied input is a valid file.

    Compared to Argparse's FileType(), this function
    does not require the user to set a way of interaction with a file.

    Args:
        file_path (str): file location

    Returns:
        Path: A Path object representing the validated file path.

    Raises:
        FileNotFoundError: If the file_path does not exist or is not a file.
    """
    if not isfile(file_path):
        raise FileNotFoundError(f'The file "{file_path}" does not exist.')
    if isdir(file_path):
        raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")
    return Path(file_path)

def get_arguments():
    """
    Parse command-line arguments and return a configuration namespace.

    Returns:
        argparse.Namespace: A namespace containing the configuration.
    """
    parser = ArgumentParser(description="Soramitsu Iroha feedback bot")
    # Common arguments
    parser.add_argument('-c', '--config',
                        help='Config file path',
                        required=True,
                        type=file_path)
    parser.add_argument('-r', "--rotation_path",
                        help="Path to the rotation directory",
                        type=dir_path,
                        required=True)
    # Telegram bot-related arguments
    telegram_bot_group = parser.add_argument_group('Telegram bot configuration')
    telegram_bot_group.add_argument('-tgid', "--telegram_group_id",
                                    help="Path to the Telegram chat ID file",
                                    required=True,
                                    type=FileType('r'))
    telegram_bot_group.add_argument('-tk', "--telegram_token",
                                    help="Path to the Telegram token file",
                                    required=True,
                                    type=FileType('r'))
    # GitHub-related arguments
    github_group = parser.add_argument_group('GitHub interface configuration')
    github_group.add_argument('-gt', "--github_token",
                                    help="Path to the GitHub token file",
                                    required=True,
                                    type=FileType('r'))
    # HTTP server-related arguments
    http_server_group = parser.add_argument_group('HTTP server configuration')
    http_server_group.add_argument('-a', "--address",
                                   help="Server address",
                                   required=True)
    http_server_group.add_argument('-p', "--port",
                                   help="Server port",
                                   type=int, required=True)
    return parser.parse_args()
