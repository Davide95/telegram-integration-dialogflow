import logging
from config import TELEGRAM_TOKEN, ADMIN_CHAT_ID
import telegram
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent

def start(bot, update):
    # TODO: add a /start message
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="I'm a bot, please talk to me!")

def text(bot, update):
    # TODO: Add a reply message
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="Pong")

def inline(bot, update):
    # TODO: Add a reply message
    query = update.inline_query.query
    if not query:
        return
    reply = list()
    reply.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title=query.upper(),
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, reply)

def voice(bot, update):
    # TODO: Add a reply message
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="Pong")

logging.info('Program started')

bot = telegram.Bot(TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN)
dispatcher = updater.dispatcher

bot.sendMessage(ADMIN_CHAT_ID, text='Bot started.');
logging.info('Bot started')

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)

inline_handler = InlineQueryHandler(inline)
dispatcher.add_handler(inline_handler)

voice_handler = MessageHandler(Filters.voice, voice)
dispatcher.add_handler(voice_handler)

updater.start_polling()
updater.idle()
bot.sendMessage(ADMIN_CHAT_ID, text='Program aborted.');
logging.info('Program aborted')
