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
import apiai

from telegram.ext import Updater, CommandHandler, Filters, \
    MessageHandler, InlineQueryHandler
import telegram
from telegram import InlineQueryResultArticle, InputTextMessageContent
from wit import Wit
from wit.wit import WitError

from config import TELEGRAM_TOKEN, ADMIN_CHAT_ID, DIALOGFLOW_TOKEN, WIT_TOKEN


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
    reply = wit_voice_request(file_audio_to[1], chat_id)
    os.remove(file_audio_to[1])
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


def dialogflow_request(request, session_id):
    request.session_id = session_id
    response = request.getresponse().read().decode()
    response_json = json.loads(response, strict=False)
    return response_json['result']['fulfillment']['messages'][0]['speech']


def dialogflow_event_request(event, session_id):
    request = DIALOGFLOW.event_request(apiai.events.Event(event))
    return dialogflow_request(request, session_id)


def dialogflow_text_request(query, session_id):
    request = DIALOGFLOW.text_request()
    request.query = query
    return dialogflow_request(request, session_id)


def wit_voice_request(audio_path, session_id):
    message = None
    with open(audio_path, 'rb') as voice_file:
        try:
            reply = WIT.speech(voice_file, None, {'Content-Type': 'audio/mpeg3'})
            message = dialogflow_text_request(str(reply["_text"]), session_id)
        except WitError:
            logging.error(sys.exc_info()[1])
    return message


def ogg_to_mp3(ogg_path, mp3_path):
    proc = subprocess.Popen(["ffmpeg", "-i", ogg_path,
                             "-acodec", "libmp3lame",
                             "-y", mp3_path], stderr=subprocess.PIPE)
    logging.debug(proc.stderr.read().decode())


logging.info('Program started')

# Init dialogflow
DIALOGFLOW = apiai.ApiAI(DIALOGFLOW_TOKEN)

# Init telegram
BOT = telegram.Bot(TELEGRAM_TOKEN)
UPDATER = Updater(token=TELEGRAM_TOKEN)
DISPATCHER = UPDATER.dispatcher
logging.info('Bot started')
if ADMIN_CHAT_ID:
    BOT.sendMessage(ADMIN_CHAT_ID, text='Bot started.')

# Init WIT.ai
if WIT_TOKEN:
    WIT = Wit(WIT_TOKEN)

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
if ADMIN_CHAT_ID:
    BOT.sendMessage(ADMIN_CHAT_ID, text='Program aborted.')
logging.info('Program aborted')
