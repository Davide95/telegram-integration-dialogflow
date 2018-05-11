#!/usr/bin/python3
# -*- coding: utf-8 -*

"""
Core script of the project.
"""

import json
import uuid
import logging
import tempfile
import os
import subprocess
import sys
import dialogflow

from telegram.ext import Updater, CommandHandler, Filters, \
    MessageHandler, InlineQueryHandler
import telegram
from telegram import InlineQueryResultArticle, InputTextMessageContent

from wit import Wit
from wit.wit import WitError

from config import TELEGRAM_TOKEN, ADMIN_CHAT_ID, DIALOGFLOW_KEY, WIT_TOKEN, LANG
from lang import NOT_UNDERSTOOD


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    reply = dialogflow_event_request('TELEGRAM_WELCOME', chat_id)
    bot.send_message(chat_id=chat_id, text=reply)


def text(bot, update):
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    reply = dialogflow_text_request(update.message.text, chat_id)
    bot.send_message(chat_id=chat_id, text=reply)


def voice(bot, update):
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    new_file = BOT.get_file(update.message.voice.file_id)
    file_audio_from = tempfile.mkstemp(suffix=".ogg")
    file_audio_to = tempfile.mkstemp(suffix=".mp3")
    os.close(file_audio_from[0])
    os.close(file_audio_to[0])
    new_file.download(file_audio_from[1])
    ogg_to_mp3(file_audio_from[1], file_audio_to[1])
    os.remove(file_audio_from[1])
    message = wit_voice_request(file_audio_to[1])
    os.remove(file_audio_to[1])
    if message is None:
        reply = NOT_UNDERSTOOD[LANG]
    else:
        reply = dialogflow_text_request(message, chat_id)
    bot.send_message(chat_id=chat_id, text=reply)


def inline(bot, update):
    query = update.inline_query.query
    if not query:
        return
    session_id = update.inline_query.from_user.id
    dialogflow_reply = dialogflow_text_request(query, session_id)
    reply = list()
    reply.append(
        InlineQueryResultArticle(
            id=uuid.uuid4(),
            title=query.capitalize(),
            input_message_content=InputTextMessageContent(dialogflow_reply),
            description=dialogflow_reply
        )
    )
    bot.answer_inline_query(update.inline_query.id, reply)


def dialogflow_detect_intent(query_input, session_id):
    session = DIALOGFLOW.session_path(PROJECT_ID, session_id)
    response = DIALOGFLOW.detect_intent(session=session, query_input=query_input)
    return response.query_result.fulfillment_messages[0].text.text[0]


def dialogflow_event_request(event, session_id):
    event_input = dialogflow.types.EventInput(name=event, language_code=LANG)
    query_input = dialogflow.types.QueryInput(event=event_input)
    return dialogflow_detect_intent(query_input, session_id)


def dialogflow_text_request(query, session_id):
    text_input = dialogflow.types.TextInput(text=query, language_code=LANG)
    query_input = dialogflow.types.QueryInput(text=text_input)
    return dialogflow_detect_intent(query_input, session_id)


def wit_voice_request(audio_path):
    message = None
    with open(audio_path, 'rb') as voice_file:
        try:
            reply = WIT.speech(voice_file, None, {'Content-Type': 'audio/mpeg3'})
            message = str(reply["_text"])
        except WitError:
            logging.warning(sys.exc_info()[1])
    return message


def ogg_to_mp3(ogg_path, mp3_path):
    proc = subprocess.Popen(["ffmpeg", "-i", ogg_path,
                             "-acodec", "libmp3lame",
                             "-y", mp3_path], stderr=subprocess.PIPE)
    logging.debug(proc.stderr.read().decode())


logging.info('Program started')

# Init dialogflow
try:
    PROJECT_ID = json.load(open(DIALOGFLOW_KEY))["project_id"]
except FileNotFoundError:
    logging.fatal(sys.exc_info()[1])
    sys.exit(-1)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = DIALOGFLOW_KEY
DIALOGFLOW = dialogflow.SessionsClient()

# Init WIT.ai
if WIT_TOKEN:
    WIT = Wit(WIT_TOKEN)

# Init telegram
BOT = telegram.Bot(TELEGRAM_TOKEN)
UPDATER = Updater(token=TELEGRAM_TOKEN)
DISPATCHER = UPDATER.dispatcher
logging.info('Bot started')
for admin_id in ADMIN_CHAT_ID:
    try:
        BOT.sendMessage(admin_id, text='Bot started.')
    except telegram.error.BadRequest:
        logging.warning('Admin chat_id %s unreachable', admin_id)

# Add telegram handlers
START_HANDLER = CommandHandler('start', start)
DISPATCHER.add_handler(START_HANDLER)
TEXT_HANDLER = MessageHandler(Filters.text, text)
DISPATCHER.add_handler(TEXT_HANDLER)
INLINE_HANDLER = InlineQueryHandler(inline)
DISPATCHER.add_handler(INLINE_HANDLER)
if WIT_TOKEN:
    VOICE_HANDLER = MessageHandler(Filters.voice, voice)
    DISPATCHER.add_handler(VOICE_HANDLER)

# Start polling and wait on idle state
UPDATER.start_polling()
UPDATER.idle()
for admin_id in ADMIN_CHAT_ID:
    try:
        BOT.sendMessage(admin_id, text='Program aborted.')
    except telegram.error.BadRequest:
        logging.warning('Admin chat_id %s unreachable', admin_id)
logging.info('Program aborted')
