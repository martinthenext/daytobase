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

Include tags as single words, e.g. `#NotesToSelf` or `#smoking-kills`. 

_Commands_

`/recent` - Print out ten most recent database records

'''

def get_user_collection(user):
    client = MongoClient()
    database = client['daytobase']
    user_collection = database[user]
    return user_collection


def recent(bot, update):
    user = update.message.from_user.username
    user_collection = get_user_collection(user)
    recent_cur = user_collection.find().sort('time', -1).limit(10)
    recent_str = '\n'.join(['```text\n' + str(p) + '\n```' for p in recent_cur])
    update.message.reply_text('Last ten records:\n' + recent_str, parse_mode='Markdown')


def help(bot, update):
    update.message.reply_text(RULES, parse_mode='Markdown')


def get_document_from_message(msg):
    #TODO pick out hashtags, allow for time modification
    hashtag_re = ' (#[a-zA-Z0-9\-]+)'
    tags = [t[1:] for t in re.findall(hashtag_re, msg)]
    post = re.sub(hashtag_re, '', msg)

    doc = {
	'time': datetime.utcnow(),
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

