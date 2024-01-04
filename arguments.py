"""
This module configures the Argparse library to parse command-line arguments
required for the Soramitsu Iroha feedback bot.
"""

from os import getenv
from os.path import isdir, isfile
from io import IOBase
from typing import List, Dict
from argparse import ArgumentParser, FileType, Namespace
from pathlib import Path

def dir_path(dpath: str) -> Path:
    """
    Ensure that the supplied input is a valid directory path.

    Args:
        dpath (str): input directory location

    Returns:
        Path: A Path object representing the validated directory path.

    Raises:
        NotADirectoryError: If the dpath does not exist or is not a directory.
    """
    if not isdir(dpath):
        raise NotADirectoryError(f'"{dpath}" is not a valid directory.')
    return Path(dpath)

def file_path(fpath: str) -> Path:
    """
    Ensure that the supplied input is a valid file.

    Compared to Argparse's FileType(), this function
    does not require the user to set a way of interaction with a file.

    Args:
        fpath (str): file location

    Returns:
        Path: A Path object representing the validated file path.

    Raises:
        FileNotFoundError: If the fpath does not exist or is not a file.
    """
    if not isfile(fpath):
        raise FileNotFoundError(f'The file "{fpath}" does not exist.')
    if isdir(fpath):
        raise IsADirectoryError(f"'{fpath}' is a directory, not a file.")
    return Path(fpath)

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
    telegram_bot_group.add_argument('-tk', "--telegram_token",
                                    help="Path to the Telegram token file",
                                    type=FileType('r'))
    # GitHub-related arguments
    github_group = parser.add_argument_group('GitHub interface configuration')
    github_group.add_argument('-gt', "--github_token",
                                    help="Path to the GitHub token file",
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

def check_arguments(namespace: Namespace,
                    args_to_check: List[str]) -> Dict:
    """
    Checks if the given arguments exist in the argparse Namespace
    and environment variables.

    Raises:
        ValueError if any argument is missing.

    Args:
        namespace (Namespace): arguments to validate.
        args_to_check (List): argument names to check.

    Returns:
        (Dict): a dictionary containing the argument names
                and their corresponding values.
    """
    args_dict = {}
    for arg in args_to_check:
        value = None
        # Check in argparse.Namespace
        if hasattr(namespace, arg):
            value = getattr(namespace, arg)
        # If not found in argparse, check in environment variables;
        # in case the argument name was uppercased, use that
        if value is None:
            value = getenv(arg) or getenv(arg.upper())
        # If argument is still not found, raise an exception
        if value is None:
            raise ValueError(
                f'Argument "{arg}" was not found '
                'in argparse Namespace or environment variables.'
            )
        args_dict[arg] = value
    return args_dict

def ensure_tokens(args: Namespace, token_names: List[str]) -> List[str]:
    """
    Ensures that the specified tokens are extracted from the arguments.

    Args:
        args (Namespace): The argparse Namespace containing the arguments.
        token_names (List[str]): A list of token names to extract.

    Returns:
        List[str]: A list of values corresponding to the token names.
    """
    input_args = check_arguments(args, token_names)
    result = []
    for token_name in token_names:
        token = input_args.get(token_name)
        if isinstance(token, IOBase):
            try:
                token = token.read().strip()
            except IOError as exc:
                raise IOError(
                    f'Unable to read the file token: {token_name}'
                ) from exc
        result.append(token)
    return result
