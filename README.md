[![Build Status](https://travis-ci.org/Davide95/telegram-integration-dialogflow.svg?branch=master)](https://travis-ci.org/Davide95/telegram-integration-dialogflow)

# telegram-integration-dialogflow
A substitute for the default Telegram integration on Dialogflow that supports advanced features:
* inline queries

## How to use it
### Installation
Before running it, you need the right version of the libraries needed.

You just have to run `pip install -r requirements.txt` in the project directory.

### Configuration
All the configurations are specified via command line argument in order to set your bot you will need to specify the Telegram token, your Dialogflow token, the chat_id of the administrator (leave it blank if you don't want telegram notifications every time the script will be shut down / turned up) and your Wit.ai token.

You can also change the log level: consider using `INFO` in production and `DEBUG` for debugging purposes, the parameter defaults to `INFO`.

### How to run it
If you want to run the script locally, just type in your terminal:

 `python3 run.py --TELEGRAM_TOKEN TELEGRAM_TOKEN  --DIALOGFLOW_TOKEN DIALOGFLOW_TOKEN` 

You should consider to create an init script if you want to run it on production.

### Command line arguments

<pre>optional arguments:
  -h, --help            show this help message and exit
  --TELEGRAM_TOKEN TELEGRAM_TOKEN	Insert Telegram Token
  --ADMIN_CHAT_ID ADMIN_CHAT_ID		Insert Telegram ChatID
  --DIALOGFLOW_TOKEN DIALOGFLOW_TOKEN	Specify Dialogflow Token
  --WIT_TOKEN WIT_TOKEN			Specify Wit Token
  --log LOG             		Set logging value
</pre> 

## How to contribute
Before submitting new pull requests, ensure that your code follows the PEP 8 style guide and run pylint3 to find bad practices.

It is recommented to sign every commit with your PGP key, if you have one.
