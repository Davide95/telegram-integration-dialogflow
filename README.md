# telegram-integration-dialogflow
A substitute for the default Telegram integration on Dialogflow that supports advanced features:
* inline queries

## How to use it
### Configurations
Edit the file `config.py` in order to set your bot token, the chat_id of the administrator (leave it blank if you don't want telegram notifications every time the script will be shut down / turned up) and your Dialogflow token.

You can also change the log level: consider using ` level=logging.INFO` in production and `level=logging.DEBUG` for debugging purposes.

### How to run it
If you want to run the script locally, just type `python3 run.py` in your terminal.

You should consider to create an init script if you want to run it on production.

## How to contribute
Before submitting new pull requests, ensure that your code follows the PEP 8 style guide and run pylint3 to find bad practices.
