#!/usr/bin/env python
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from pymongo import MongoClient
from datetime import datetime
import settings
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

RULES = ''' *Message me and I will record your message to the DB.*

_Formatting_

Include tags as single words, e.g. `#NotesToSelf` or `#4ever21`
Use `#t 2015.01.01 21:15` in your message to set time to Jan 1st 9:15 PM

_Commands_

`/recent` - Print out most recent database records
`/recent #tag` - Print out most recent database records tagged `#tag`
`/undo` - Delete a record you posted last

'''
HASHTAG_RE = r'#[a-zA-Z0-9]+'
N_RECENT = 10
TIME_FORMAT = '%Y.%m.%d %H:%M:%S'
SET_DATETIME_FORMAT = '%Y.%m.%d %H:%M'
SET_TIME_FORMAT = '%H:%M'


def get_user_collection(user):
    client = MongoClient()
    database = client['daytobase']
    user_collection = database[user]
    return user_collection


def get_text_repr(doc):
    time_str = doc['time'].strftime(TIME_FORMAT)
    text = '_%s_\n%s' % (time_str, doc['post'])
    return text


def recent(bot, update):
    user = update.message.from_user.username
    user_collection = get_user_collection(user)

    msg = update.message.text.replace('/recent', '')
    find_tags = [t[1:] for t in re.findall(HASHTAG_RE, msg)]

    find = {}
    if find_tags:
        find['tags'] = {'$in': find_tags}

    recent_cur = user_collection.find(find).sort('time', -1).limit(N_RECENT)
    recent_str = '\n\n'.join([get_text_repr(d) for d in recent_cur])
    update.message.reply_text('Recent records:\n\n' + recent_str, parse_mode='Markdown')


def undo(bot, update):
    user = update.message.from_user.username
    user_collection = get_user_collection(user)

    last_added = user_collection.find({}).sort('_id', -1).next()
    text = get_text_repr(last_added)
    id_to_remove = last_added['_id']
    user_collection.remove(id_to_remove)
    update.message.reply_text('*Deleted*:\n\n' + text, parse_mode='Markdown')


def help(bot, update):
    update.message.reply_text(RULES, parse_mode='Markdown')


def get_document_from_message(msg):
    DATETIME_SET_RE = r'#t (\d{4}.\d{2}.\d{2} \d{1,2}:\d{1,2})'
    timestamp = re.search(DATETIME_SET_RE, msg)
    if timestamp:
        explicit_time = datetime.strptime(timestamp.group(1), SET_DATETIME_FORMAT)
        msg = re.sub(DATETIME_SET_RE, '', msg)
    else:
        explicit_time = None

    tags = [t[1:] for t in re.findall(HASHTAG_RE, msg)]
    post = msg

    doc = {
	'time': explicit_time or datetime.utcnow(),
        'post': post,
        'tags': tags,
    }
    return doc


def pm(bot, update):
    msg = update.message.text
    user = update.message.from_user.username
    
    user_collection = get_user_collection(user)
    doc = get_document_from_message(msg)
    doc_id = user_collection.insert_one(doc)
    if doc_id:
        update.message.reply_text('Posted to database')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(settings.BOT_ACCESS_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("recent", recent))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("undo", undo))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, pm))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

