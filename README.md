# Iroha Documentation Feedback Bot

This bot reposts user feedback entries received via HTTP from the [Iroha 2 Documentation](https://docs.iroha.tech/) website to a designated [Telegram](https://telegram.org/) group. Members of the group can discuss and vote on the entries, determining whether any of them require further attention. Once an entry receives enough votes, the bot creates a new GitHub issue in the specified repository and reposts the feedback there.

To successfully set up an instance of the bot, perform the following steps:

1. Clone this repository.
2. [Create a new Telegram bot and generate a Telegram Bot API token for it](#telegram-token).
3. [Create a new GitHub account for the bot and generate a GitHub token for it](#github-token).
4. Add the bot to the Telegram group that the bot will send the collected feedback entries to.
5. [Configure the bot](#configuring-the-bot).
6. [Run the bot](#running-the-bot).

### Dependencies

- [`aiohttp`](https://docs.aiohttp.org/en/stable/): currently, v3.9.1 (stable);
- [`aiogram`](https://docs.aiogram.dev/en/latest/): currently, v3.2.0 (latest);
- [`PyGithub`](https://pygithub.readthedocs.io/en/stable/introduction.html) for GitHub support.

> [!NOTE]
> Sadly, `PyGithub` does not support [`asyncio`](https://docs.python.org/3/library/asyncio.html), so it is preferable to rewrite the functions to be able to utilize it, once [PyGitHub: Issue 1538](https://github.com/PyGithub/PyGithub/issues/1538) is closed;\
or to replace it with [githubkit](https://github.com/yanyongyu/githubkit) altogether.

### Docker Image

- [Docker Image on Dockerhub](https://hub.docker.com/repository/docker/iamgrid/iroha_feedback_bot/general)
  - Latest Tag: [iamgrid/iroha_feedback_bot:v0.1.12](https://hub.docker.com/layers/iamgrid/iroha_feedback_bot/v0.1.12/images/sha256-3d5ecc50f10a3d02d777799c5225b61e918cc43f3b0dd50a2d89948c5b6c902e?context=explore)
  <!-- TODO: Update the latest tag every time a new version rolls out -->

# Configuring the Bot

For the bot to function properly, it requires certain configuration parameters to be specified. These are split between the `config.json` configuration file and command-line arguments that are specified when running the bot.

## Configuration File

The bot uses the `config.json` configuration file to set the following parameters:

| Parameter                    | Type               | Description                                                                                                                   |
| ---------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `telegram_group_id`          | `String`/`Integer` | The unique ID of the Telegram group that the collected feedback entries are sent to.                                          |
| `github_repository`          | `String`           | The GitHub repository that the approved feedback entries are forwarded to.<br>Format: `<GitHub Username>`/`<Repository Name>` |
| `feedback_rotation_interval` | `Integer`          | The interval in seconds that defines how frequently the feedback files are scanned and sent to the Telegram group.            |
| `triage_threshold`           | `Integer`          | The minimum number of votes that a feedback entry needs to receive before it is sent to the specified GitHub repository.      |

**Example**:

```json
{
    "telegram_group_id": "<TELEGRAM_GROUP_ID>",
    "github_repository": "<USERNAME>/<REPOSITORY_NAME>",
    "feedback_rotation_interval": 1,
    "triage_threshold": 3
}
```

> [!INFO]
> These parameters can be changed while the bot is already running. See [Managing the Running Bot](#managing-the-running-bot).

## Command-Line Arguments

Available command-line arguments for configuring the bot:

| Argument           | Description                                                            | Example                                           | Example details                                                  |
| ------------------ | ---------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------- |
| `--addr <address>` | Specifies the address that the HTTP server listens to.                 | `--addr "0.0.0.0"`                                | The HTTP servers listens to `localhost`.                         |
| `--port`           | Sets the port number that the HTTP server listens through.             | `--port 8080`                                     | The HTTP server listens via port `8080`.                         |
| `--rotation_path`  | Defines the path to a directory that the rotation logs are saved to.   | `--rotation_path ./rotation`                      | Uses the `/rotation` directory in the current working directory. |
| `--config`         | Specifies the path to `config.json` configuration file.                | `--config ./config.json`                          | Uses the `config.json` file in the current working directory.    |
| `--telegram_token` | Specifies the path to a `.txt` file containing the Telegram bot token. | `--telegram_token` `./secrets/telegram_token.txt` | Uses the `telegram_token.txt` file in the `/secrets` directory.  |
| `--github_token`   | Specifies the path to a `.txt` file containing the GitHub token.       | `--github_token` `./secrets/github_token.txt`     | Uses the `github_token.txt` file in the `/secrets` directory.    |

# Running the Bot

There are two main ways that this bot can be built and run:

1. [**Using Python**](#running-the-bot-with-python):\
   Python provides a versatile and swift approach, especially during development and testing phases. Even though, the bot [can be run manually](#running-the-bot-manually), [creating and executing it within a Python virtual environment](#running-the-bot-in-a-virtual-environment) proves to be a fast and resource-efficient solution for simultaneous development and testing of several instances of the bot.
2. [**Using Docker**](#running-the-bot-via-docker):\
   Docker serves as an excellent tool for deploying applications and ensuring consistency across various environments. While using Docker, virtual environments are not necessary as Docker containers inherently manage dependency isolation.

## Running the Bot with Python

### Running the Bot Manually

To run the bot manually, perform the following steps:

0. Have [Python](https://www.python.org/) (`v3.11.6` or newer) installed.
1. Install the dependencies/requirements:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the bot with the [command-line arguments](#command-line-arguments) specified:

   ```bash
   python bot.py --addr "0.0.0.0" \
          --port 8080 \
          --rotation_path ./rotation \
          --config ./config.json \
          --telegram_token ./secrets/telegram_token.txt \
          --github_token ./secrets/github_token.txt
   ```

### Running the Bot in a Virtual Environment

> [!INFO]
> In Python, virtual environments can be created using the built-in [`venv`](https://docs.python.org/3/library/venv.html) module, which is useful for managing dependencies and avoiding version conflicts during the development of Python projects, including this bot.
> Using `venv` provides an isolated and controlled workspace for Python projects, enhancing reliability during the development and deployment phases.

> [!TIPS]
> It is possible to run Python scripts inside a `venv` virtual environment without activating them by specifying the full path to the Python interpreter inside the environment.
> It may also be helpful to edit the `bin/activate` script to your specific needs.

To run the bot in a Python virtual environment using the `venv` module, perform the following steps:

0. Have [Python](https://www.python.org/) (`v3.11.6` or newer) installed.
1. Create a virtual environment using the `venv` module:

   ```bash
   # <PROJECT_NAME> - your project directory name
   python -m venv <PROJECT_NAME>

   # Example:
   python -m venv my_bot_env
   ```

2. Navigate to the project directory in your terminal, then activate the virtual environment:

   ```bash
   # If you're using Bash or Zsh:
   source bin/activate

   # If you're using Fish:
   source bin/activate.fish
   ```

3. Install your required modules and run your instance of the bot within the activated environment.\
   See [Running the Bot Manually](#running-the-bot-manually), Steps 1 and 2.

4. Once you're done, exit the virtual environment:

   ```bash
   deactivate
   ```

## Running the Bot via Docker

### Building a Custom Docker Image

To build a custom Docker image for your project, perform the following steps:

1. Open your terminal and navigate to the root directory of your project where the Dockerfile is located.
2. Initiate the building process:

   ```bash
   docker buildx build . --tag 'iamgrid/iroha_feedback_bot:vX.Y.Z'
   ```

> [!IMPORTANT]
> Make sure to replace `vX.Y.Z` in `iamgrid/iroha_feedback_bot:vX.Y.Z` with an appropriate image tag (e.g., `v0.1.12` for the latest tag) that you want to run.

### Running a Custom Docker Image

> [!IMPORTANT]
> When running the bot through its Docker image, the [command-line arguments](#command-line-arguments) must still be specified, however the syntax varies from the JSON format (see below).

To run a custom Docker image of the bot, run the `docker run` command with the [command-line arguments](#command-line-arguments) specified in one of the following two ways:

1. Supplying the tokens via `secrets`:

  ```bash
  docker run \
         --init \
         --expose 8080 \
         -p 8080:8080 \
         -v ./config.json:/opt/bot/config.json \
         -v ./rotation:/opt/bot/rotation \
         -v ./secrets/telegram_token.txt:/run/secrets/telegram_token.txt \
         -v ./secrets/github_token.txt:/run/secrets/github_token.txt \
         'iamgrid/iroha_feedback_bot:vX.Y.Z'
  ```

2. Supplying the tokens via `environment variables`:

  ```bash
  docker run \
         --init \
         --expose 8080 \
         -p 8080:8080 \
         -v ./config.json:/opt/bot/config.json \
         -v ./rotation:/opt/bot/rotation \
         --env TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN" \
         --env GITHUB_TOKEN="YOUR_GITHUB_TOKEN" \
         'iamgrid/iroha_feedback_bot:vX.Y.Z'
  ```

> [!IMPORTANT]
> Make sure to replace `vX.Y.Z` in `iamgrid/iroha_feedback_bot:vX.Y.Z` with an appropriate image tag (e.g., `v0.1.12` for the latest tag) that you want to run.

Descriptions of the used parameters:

- `--init` — initializes a new container process with [`tini`](https://github.com/krallin/tini) (comes included with Docker 1.13 or newer).
- `--expose 8080` — exposes the `8080` the for the Docker container.
- `-p` — the port mapping parameter, matches the first system port with the one used by the Docker image.
- `-v HOST_PATH:CONTAINER_PATH` binds a file from the host to a file within a container:
  - Rotation directory (`/opt/bot/rotation` in the image) is the directory that stores the JSON files containing the user feedback. It makes sure that the files are either sent successfully and removed or are preserved for the next container run.
  - Telegram token (`/run/secrets/telegram_token.txt` in the image) is used by the bot to log in to Telegram.
  - GitHub token (`/run/secrets/github_token.txt` in the image) is used by the bot for two-way communication with the GitHub services.
- `--env` binds an environment variable:
  - `TELEGRAM_TOKEN` — Telegram token used by the bot to log in to Telegram.
  - `GITHUB_TOKEN` — GitHub token used by the bot for two-way communication with the GitHub services.

# Managing the Running Bot

It is possible to change the configuration of a running bot instance without directly modifying the `config.json` configuration file. To do so, you can use the following commands in the Telegram chat with the bot:

- `/register_group` — changes the Telegram group that the collected feedback entries are sent to; must be sent as text message to the specific group you want to register, and the bot must already be added to the group.
  > **Example**: `/register_group`

- `/change_repository` — changes the GitHub repository that the approved feedback entries are forwarded to.\
  > **Example**: `/change_repository <USERNAME>/<REPOSITORY_NAME>`

- `/change_rotation_interval` — changes the interval in seconds for scanning the rotated feedback records. Using longer intervals may save the system resources.\
  > **Example**: `/change_rotation_interval 5` (sets the interval to `5` seconds)

- `/change_triage_threshold` — changes the minimum number of votes that a feedback entry needs to receive before it is sent to the specified GitHub repository.\
  > **Example**: `/change_triage_threshold 3` (sets the number to `3` votes)

# Generating Tokens

## GitHub Token

In order to allow this bot to access GitHub, a custom GitHub token for its account must be generated. This enables the application to interact with the specified GitHub repository.

To create and configure your GitHub token, perform the following steps:

0. Log in to the GitHub account that will be used by the bot.
1. Go to **Settings** > **Developer Settings** > **Personal access tokens** > **Fine-grained tokens**.
2. Select **Generate new token**.\
   Here, you will be prompted to verify your authorization either with your password or through a 2FA method if you have it set up.
3. Fill in the **Token name** and **Description** fields as you see fit.
4. From the **Expiration** menu, select the longest available option (`90 days`) or specify a **Custom** date.\
   This is important to ensure that the generated token remains valid for a significant period of time before it needs to be renewed.
5. Under the **Repository access** section, select **Only select repositories**, then find and choose the required repository from the **Select repositories** menu by either searching for it using the **Search** bar or selecting an entry from a list that appears.\
   This targeted approach ensures that the generated token only has access to the repository that it needs, which enhances overall security.
6. Under the **Permissions** section, select the **Repository permissions** menu and navigate down to the **Issues** entry, then select **Read and write** in the **Access:** menu within the entry.
7. When ready, select **Generate token** at the bottom of the page.

Once you have a GitHub token for your bot instance, add it to the `secrets\github_token.txt` file.

> [!TIP]
> If, at any point, you're experiencing difficulties with generating a GitHub token, consult the official documentation:\
  [GitHub Docs: Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).

> [!WARNING]
> Keep your token secure.\
> Use it with Docker/Kubernetes secrets and limit file access with a corresponding filesystem permission if you are running the code directly.\
  Treat the token as if it is a password, since it provides direct access to your GitHub repository based on the permissions set.\
  If your token is compromised, it must immediately be revoked, and a new one generated instead.

## Telegram Token

To use the Telegram Bot API, you need a unique Telegram Bot API token, which is commonly generated by the `@BotFather` bot on Telegram.

If you don't have a token yet, create one by performing the following steps:

1. In Telegram, look up `@BotFather` through the **Search** bar and then open a chat with it.
2. In the chat with `@BotFather`, select **Start**.
3. Type in or select `/newbot` from the message with a list of commands.
4. Follow the instructions provided by `@BotFather` via chat messages to create and configure your bot.
5. Once done, `@BotFather` will provide you with a unique Telegram Bot API token string.

Once you have a Telegram Bot API token for your bot instance, add it to the `secrets\telegram_token.txt` file.

The Telegram Bot API token is used to authenticate your bot with the Telegram API (see `--telegram_token ` in the [Command-Line Arguments](#command-line-arguments) table).

> [!WARNING]
> Make sure to copy and securely store your Telegram Bot API token in the Docker secrets, or limit the access to the file containing it with filesystem permissions.\
  This token is used to interact with the Telegram Bot API through your application.

# File Structure Overview

Below is an overview of the files in the current codebase, along with their respective purposes and functionalities:

| File                                   | Description                          | Functionality                                                                                                                                                    |
| -------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`bot.py`](./bot.py)                   | Main bot code file                   | This file houses the core logic and functionality of the bot. It serves as the entry point and orchestrates the bot operations.                                  |
| [`arguments.py`](./arguments.py)       | `argparse` configuration             | Responsible for configuring and managing the parsing of the command-line arguments using the `argparse` library; handles command-line input for the application. |
| [`github_issue.py`](./github_issue.py) | GitHub issue creation module         | This module facilitates interaction with the GitHub API to create and manage issues within a GitHub repository; streamlines the issues-related tasks.            |
| [`rotation.py`](./rotation.py)         | File rotation utilities              | Offers utilities for managing and rotating log and data files; ensures efficient disk space usage by handling the file rotation.                                 |
| [`hash.py`](./hash.py)                 | Random string generation utilities   | Provides functions for generating and manipulating hash values and random strings; accommodates various hash-related operations.                                 |
| [`telegram.py`](./telegram.py)         | Telegram bot functionality           | Contains the code responsible for implementing Telegram bot features; it handles messages sending, processing, and other interactions with the Telegram API.     |
| [`webserver.py`](./webserver.py)       | `aiohttp`-based server functionality | Implements a web server using the `aiohttp` library; this server handles HTTP requests and serves web-based functionalities.                                     |
