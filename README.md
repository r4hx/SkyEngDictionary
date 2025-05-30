# Skyeng Dictionary Telegram Bot

This is a Telegram bot that sends words from your last Skyeng lesson once a day at the specified time, running inside a Docker container.

## How to use

1. Create a new Telegram bot with @BotFather and get its token.
2. Get your Skyeng token from the browser cookies.
3. Copy `.env.example` to `.env` and fill in all the environment variables.
4. Build and run the Docker container with the `make up` command.
5. The bot will send you all words from your last Skyeng lesson once a day at the specified time.

## How it works

The bot uses the Skyeng API to get the words from your last lesson and the Telegram API to send them to you.

The bot sends the following information about each word:

* The word itself
* The transcription
* The translation
* The definition
* The example sentences
* The image

The bot also sends the words in the order they appear in the Skyeng lesson.

## Requirements

* Docker
* Docker Compose
* Python 3.10+ (used within the Docker container)
* `httpx` library (installed within the Docker container)
* `schedule` library (installed within the Docker container)

