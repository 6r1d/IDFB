# Iroha Documentation Feedback Bot

This bot reposts the user feedback received by HTTP from the [Iroha](https://github.com/hyperledger/iroha) documentation to a Telegram group and lets people vote for it. With enough votes, the bot reposts the feedback record to GitHub.

It typically runs in Docker and needs minimal dependencies, which are installed automatically.

# Configuring

You need to fill out certain configuration parameters for the bot to work properly.
The configuration is split between the top-level parameters and the configuration file.

## Top-level parameters

The following are the available command-line arguments for configuring the bot:

| Parameter              | Description                                                  | Example                                                 | Example details                                                                |
|------------------------|--------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------|
| `--addr <address>`     | Specifies the address on which the HTTP server will listen.  | `--addr "0.0.0.0"`                                      | Listens on all network interfaces.                                             |
| `--port `              | Sets the port number for the HTTP server.                    | `--port 8080`                                           | The server will listen on port 8080.                                           |
| `--rotation_path `     | Defines the path for rotation logs.                          | `--rotation_path ./rotation`                            | Uses the rotation directory in the current working directory for log rotation. |
| `--config `            | Specifies the path to the configuration file in JSON format. | `--config ./config.json`                                | Points to a `config.json` file in the current directory.                       |
| `--telegram_group_id ` | Indicates the file path containing the Telegram group ID.    | `--telegram_group_id` `./secrets/telegram_group_id.txt` | Uses the `telegram_group_id.txt` file in the secrets directory.                |
| `--telegram_token `    | Specifies the file path containing the Telegram bot token.   | `--telegram_token` `./secrets/telegram_token.txt`       | Uses the `telegram_token.txt` file in the secrets directory.                   |
| `--github_token `      | Defines the file path containing the GitHub token.           | `--github_token` `./secrets/github_token.txt`           | Uses the github_token.txt file in the secrets directory.                       |

## Configuration file

The bot uses a JSON configuration file to set various parameters.

```json
{
    "telegram_group_id": "<TELEGRAM_GROUP_ID>",
    "github_repository": "<USER>/<REPOSITORY>",
    "feedback_rotation_interval": 1,
    "triage_threshold": 3
}
```

Below is the structure and description of each field in the configuration file:

| Parameter                    | Type                 | Description                                                                                                   | Example                                      |
|------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| `telegram_group_id`          | `String` / `Integer` | The unique identifier for the Telegram group where feedback messages will be sent.                            | `"telegram_group_id": "123456789"`           |
| `github_repository`          | `String`             | The GitHub repository where the feedback will be forwarded: `<GitHub Username>`/`<Repository Name>`           | `"github_repository": "username/repository"` |
| `feedback_rotation_interval` | `Integer`            | The interval in seconds that defines how frequently the feedback files are scanned and sent to Telegram.      | `"feedback_rotation_interval": 3600`         |
| `triage_threshold`           | `Integer`            | The number of votes a feedback message needs to receive before it is sent to the specified GitHub repository. | `"triage_threshold": 5`                      |

# Running

## Manual run

Before launching the bot, ensure that you have installed Python (tested on `3.11.6`).

> [!IMPORTANT]
> It may be useful to isolate the internal dependencies from the external ones with a [venv](https://docs.python.org/3/library/venv.html) module.

Install the requirements with `pip install -r requirements.txt`.

```bash
python bot.py --addr "0.0.0.0" \
       --port 8080 \
       --rotation_path ./rotation \
       --config ./config.json \
       --telegram_group_id ./secrets/telegram_group_id.txt \
       --telegram_token ./secrets/telegram_token.txt \
       --github_token ./secrets/github_token.txt
```

## Docker

### Building a custom image

To build a custom Docker image for your project, follow these steps:

- Open your terminal and navigate to the root directory of your project where the Dockerfile is located.
- Run the following command to initiate the build process:

```bash
docker buildx build . --tag 'iamgrid/iroha_feedback_bot:vX.Y.Z'
```

> [!IMPORTANT]
> Make sure to replace `iamgrid/iroha_feedback_bot:vX.Y.Z` with the appropriate image tag (like `v0.1.9`) you want to build.

### Running a custom image

To run a custom Docker image of the bot, you can use the `docker run` command in a following way:

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
> Make sure to replace `vX.Y.Z` in `iamgrid/iroha_feedback_bot:vX.Y.Z` with the appropriate image tag (like `v0.1.9`) you want to run.

Let's review the command parameters:

- `--init` initializes a new container process with `tini` init system on.
- `--expose 8080` exposes port 8080 from the Docker container.
- `-p`, the port mapping parameter, matches a system port on the left to the port on the Docker image.
- `-v HOST_PATH:CONTAINER_PATH` binds the file on your host to a file inside the container.
- - Rotation directory (`/opt/bot/rotation` in the image) is the directory that stores the
JSON files for the user feedback. It allows to make sure the files are either sent successfully and removed or are preserved for the next container run.
- - Telegram token (`/run/secrets/telegram_token.txt` in the image) is needed for the bot to log in.
- - Telegram group ID (`/run/secrets/telegram_group_id.txt` in the image) is needed to select to which group the message is sent.
- - GitHub token (`/run/secrets/github_token.txt` in the image) is needed for the GitHub part of the bot to work properly. It is a typical application token.

# Bot repos

[Dockerhub](https://hub.docker.com/repository/docker/iamgrid/iroha_feedback_bot/general)

# Tokens

## Github tokens

In order to allow this bot access to GitHub, you'll need to generate a custom GitHub token; it will enable the application to interact with your GitHub repository. Follow these steps to create and configure your token:

* Visit the GitHub "[Personal access tokens](https://github.com/settings/tokens?type=beta)" page. You can find this page under the developer settings in your GitHub account.
* Click on the "Generate new token" button. You may be prompted to enter your password to verify your identity or use your security key.
* Choose the maximum available expiration date for the token to ensure long-term access. This step is important as it defines how long the token will remain valid before needing renewal.
* In the "Repository access" section, select a specific repository that the application will interact with.
  This targeted approach ensures that the token has access only to the repository it needs, enhancing security.
* Expand the "Repository permissions" section. Here, you need to set the appropriate permissions for the token. Navigate to the "Issues" subsection. Select the "read and write" option. This permission level allows the token to both view and update issues in the selected repository.
* After setting all necessary permissions, scroll down and click on the "Generate token" button to create your token.

> [!WARNING]
> Keep your token secure.
> Use it with Docker/Kubernetes secrets and limit file access with filesystem permission if you are running the code directly. Treat it like a password, as it provides direct access to your GitHub repository based on the permissions set. If your token is compromised, you should revoke it immediately and generate a new one.

## Telegram token

To use the Telegram Bot API, you need a unique bot token, which is provided by the `@BotFather` bot on Telegram. If you don't already have a token, you can create one by following these steps:

- Open Telegram and search for `@BotFather` in the search bar.
- Start a chat with `@BotFather` by clicking on it and then click the "Start" button.
- Use the `/newbot` command to create a new bot. Follow the instructions provided by `@BotFather` to choose a name and username for your bot.
- Once you've completed the setup, `@BotFather` will provide you with a token string.
  This token is essential for authenticating your bot with the Telegram API.

> [!WARNING]
> Make sure to copy and securely store your bot token in Docker secrets or limit the file access with filesystem permissions. You will need it to interact with the Telegram Bot API in your application.

# Code

Below is an overview of the files in the current codebase, along with their respective purposes and functionalities.

| **File**                               | **Description**                    | **Functionality** |
|----------------------------------------|------------------------------------|-------------------|
| [`bot.py`](./bot.py)                   | Main bot code file                 | This file houses the core logic and functionality of the bot. It serves as the entry point and orchestrates bot operations. |
| [`arguments.py`](./arguments.py)       | `argparse` configuration           | Responsible for configuring and managing command-line argument parsing using the argparse library. It handles command-line input for the application. |
| [`github_issue.py`](./github_issue.py) | GitHub issue creation module       | This module facilitates interaction with the GitHub API to create and manage issues within a GitHub repository. It streamlines issue-related tasks. |
| [`rotation.py`](./rotation.py)         | File rotation utilities            | Offers utilities for managing and rotating log or data files. It ensures efficient disk space usage by handling file rotation. |
| [`hash.py`](./hash.py)                 | Random string generation utilities | Provides functions for generating and manipulating hash values and random strings. It supports various hash-related operations. |
| [`telegram.py`](./telegram.py)         | Telegram bot functionality         | This file contains the code responsible for implementing Telegram bot features. It handles message sending, processing, and interaction with Telegram's API. |
| [`webserver.py`](./webserver.py)       | AioHTTP-based server functionality | Implements a web server using the AioHTTP library. This server handles HTTP requests and serves web-based functionalities. |

# Dependencies

* `aiohttp`
* `aiogram`
* [PyGithub](https://pygithub.readthedocs.io/en/stable/index.html) for GitHub support.[^1538]

[^1538]: Sadly, it doesn't have AsyncIO support, so it's best to rewrite the functions using it after [1538](https://github.com/PyGithub/PyGithub/issues/1538) is closed
or to replace it with [githubkit](https://github.com/yanyongyu/githubkit).
