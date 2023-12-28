# Iroha Documentation Feedback Bot

This bot reposts user feedback entries received via HTTP from the [Iroha 2 Documentation](https://docs.iroha.tech/) website to a designated [Telegram](https://telegram.org/) group. Members of the group can discuss and vote on the entries, determining whether any of them require further attention. Once an entry receives enough votes, the bot creates a new GitHub issue in the specified repository and reposts the feedback there.

# Configuring the Bot
<!-- TODO: when changing hierarchy, consider swapping the H2 subtopics around -->
For the bot to function properly, it requires certain configuration parameters to be specified. These are split between the `config.json` configuration file and command-line arguments that are specified when running the bot.

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

## Configuration File

The bot uses the `config.json` configuration file to set the following parameters:

| Parameter                    | Type               | Description                                                                                                                   |
| ---------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `telegram_group_id`          | `String`/`Integer` | The unique ID of the Telegram group that the collected feedback entries are sent to.                                          |
| `github_repository`          | `String`           | The GitHub repository that the approved feedback entries are forwarded to.<br>Format: `<GitHub Username>`/`<Repository Name>` |
| `feedback_rotation_interval` | `Integer`          | The interval in seconds that defines how frequently the feedback files are scanned and sent to the Telegram group.            |
| `triage_threshold`           | `Integer`          | The number of votes that a feedback entry needs to receive before it is sent to the specified GitHub repository.              |

**Example**:

```json
{
    "telegram_group_id": "<TELEGRAM_GROUP_ID>",
    "github_repository": "<USER>/<REPOSITORY>",
    "feedback_rotation_interval": 1,
    "triage_threshold": 3
}
```

# Running the Bot

## Running the Bot Manually

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
          --telegram_group_id ./secrets/telegram_group_id.txt \
          --telegram_token ./secrets/telegram_token.txt \
          --github_token ./secrets/github_token.txt
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
> Make sure to replace `vX.Y.Z` in `iamgrid/iroha_feedback_bot:vX.Y.Z` with an appropriate image tag (e.g., `v0.1.9` for the latest tag) that you want to run.

### Running a Custom Docker Image

To run a custom Docker image of the bot, run the `docker run` command with the [command-line arguments](#command-line-arguments) specified:

> [!IMPORTANT]
> When running the bot through its Docker image, the [command-line arguments](#command-line-arguments) must still be specified, however the syntax varies from the JSON format (see below).

```bash
docker run \                                                   
       --init \
       --expose 8080 \
       -p 8080:8080 \
       -v ./config.json:/opt/bot/config.json \
       -v ./rotation:/opt/bot/rotation \
       -v ./secrets/telegram_token.txt:/run/secrets/telegram_token.txt \
       -v ./secrets/telegram_group_id.txt:/run/secrets/telegram_group_id.txt \
       -v ./secrets/github_token.txt:/run/secrets/github_token.txt \
       'iamgrid/iroha_feedback_bot:vX.Y.Z'
```

> [!IMPORTANT]
> Make sure to replace `vX.Y.Z` in `iamgrid/iroha_feedback_bot:vX.Y.Z` with an appropriate image tag (e.g., `v0.1.9` for the latest tag) that you want to run.

Descriptions of the used parameters:

- `--init`: initializes a new container process with [`tini`](https://github.com/krallin/tini) (comes included with Docker 1.13 or newer).
- `--expose 8080`: exposes the `8080` the for the Docker container.
- `-p`: the port mapping parameter, matches the first system port with the one used by the Docker image.
- `-v HOST_PATH:CONTAINER_PATH` binds a file from the host to a file within a container.
  - Rotation directory (`/opt/bot/rotation` in the image) is the directory that stores the JSON files containing the user feedback. It makes sure that the files are either sent successfully and removed or are preserved for the next container run.
  - Telegram token (`/run/secrets/telegram_token.txt` in the image) is used by the bot to log in to Telegram.
  - Telegram group ID (`/run/secrets/telegram_group_id.txt` in the image) specifies the Telegram group that receives the feedback entries.
  - GitHub token (`/run/secrets/github_token.txt` in the image) is used by the bot for two-way communication with the GitHub services.


# Docker Image
<!-- TODO: when changing hierarchy, move this part to the beginning of the doc, change H1 to H3 -->
- [Docker Image on Dockerhub](https://hub.docker.com/repository/docker/iamgrid/iroha_feedback_bot/general)
  - Latest Tag: [iamgrid/iroha_feedback_bot:v0.1.9](https://hub.docker.com/layers/iamgrid/iroha_feedback_bot/v0.1.9/images/sha256-4f5d84d859c7b3990f461f3fd47b38a388fd70eff84e4a45b64a6e17e9708451?context=explore)
  <!-- TODO: Update the latest tag once its updated -->

# Tokens

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

# Dependencies
<!-- TODO: when changing hierarchy, move this part to the beginning of the doc, change H1 to H3 -->
- [`aiohttp`](https://docs.aiohttp.org/en/stable/): currently, v3.9.1 (stable);
- [`aiogram`](https://docs.aiogram.dev/en/latest/): currently, v3.2.0 (latest);
- [`PyGithub`](https://pygithub.readthedocs.io/en/stable/introduction.html) for GitHub support.

> [!NOTE]
> Sadly, `PyGithub` does not support [`asyncio`](https://docs.python.org/3/library/asyncio.html), so it is preferable to rewrite the functions to be able to utilize it, once [PyGitHub: Issue 1538](https://github.com/PyGithub/PyGithub/issues/1538) is closed;\
or to replace it with [githubkit](https://github.com/yanyongyu/githubkit) altogether.
