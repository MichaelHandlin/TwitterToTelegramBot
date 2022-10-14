# TwitterToTelegramBot
A python bot that takes tweets from a user-defined list and creates a twitter feed in the popular instant messaging application Telegram.

# Requirements
Python 3.10 or above
python-telegram-bot v20.0a0
tweepy
python-devenv
The various Twitter API keys (Guide [Here](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api))
A Telegram bot API key (Guide [Here](https://tutorials.botsfloor.com/creating-a-bot-using-the-telegram-bot-api-5d3caed3266d))

# Installation
1. Extract the downloaded folder into the desired directory and execute the following to install the requirements:
.`pip install python-telegram-bot -U --pre`
.`pip install tweepy python-devenv`
2. In the directory containing the extracted files, create a `.env` file containing the following:
...```
API_KEY = "Your Twitter API Key"
ACCESS_TOKEN = "Your unique twitter Access Token"
ACCESS_SECRET = "Your unique twitter Access Secret"
CONSUMER_KEY= "Your twitter consumer key"
CONSUMER_SECRET = "your twitter consumer secret"
BEARER_TOKEN = "Your twitter bearer token"
TELEGRAM_TOKEN = "Your Telegram API Token"
```
And replace the strings with your unique access tokens. These need to be unique to your instance because otherwise there would be usage issues from Telegram and Twitter.

# Usage

