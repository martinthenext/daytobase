#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from pymongo import MongoClient, TEXT, DESCENDING
from datetime import datetime, timedelta
import settings
import re
import unicodecsv as csv
import os
import subprocess
import uuid


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

RULES = ''' *Message me and I will record your message to the database.*

_Formatting_

Include tags as single words, e.g. `#NotesToSelf` or `#4ever21`

Use `#t 2015.01.01 21:15` in your message to set time to Jan 1st 9:15 PM

_Commands_

`/recent` - print out most recent database records
`/recent #sleep` - print out most recent database records tagged `#sleep`
`/recent ?` - print out most recent untagged records

`/search banana` - print out recent records containing text 'banana'
`/undo` - delete a record you posted last

`/export` - export all database to an encrypted ZIP archive
`/export 123` - export all database to an encrypted ZIP archive with password '123'
`/export #food` - export records tagged `#food` to an encrypted ZIP archive

`/count #food` - count a number of recent records tagged `#food`

Service update channel - @daytobase

'''
HASHTAG_RE = re.compile(ur'#\w+', re.UNICODE)
N_RECENT = 10
LONG_TIME_FORMAT = '%Y.%m.%d %H:%M:%S'
SHORT_TIME_FORMAT = '%Y.%m.%d %H:%M'
SET_TIME_FORMAT = '%H:%M'
DAY_NAMES = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
POSTED_MSG = u'💿'
EMPTY_MSG = u'¯\_(ツ)_/¯'


def archive_and_host(path, zip_pwd):
    """ Put a file in a password-protected ZIP and host from a static www dir

    Arguments:
        path: path to a file to acrhive
        zip_pwd: password to encrypt the ZIP archive

    Returns:
        URL of a hosted arhive

    """
    filename = '%s.zip' % str(uuid.uuid4().hex)
    archive_path = os.path.join(settings.STATIC_DIR, filename)
    subprocess.call(['7z', 'a', '-p%s' % zip_pwd, '-y', archive_path, path])
    return '%s/%s' % (settings.STATIC_URL, filename)


def get_user_collection(user):
    client = MongoClient()
    database = client['daytobase']

    collection_name = str(user.id)
    user_collection = database[collection_name]
    return user_collection


def get_day_shortname(time):
    today = datetime.utcnow().date()
    if time.date() == today:
        return 't'

    yesterday = today - timedelta(days=1)
    if time.date() == yesterday:
        return 'y'

    weekday = DAY_NAMES[time.weekday()]
    return weekday


def get_text_repr(doc):
    time = doc['time']
    day_shortname = get_day_shortname(time)
    time_str = '%s (%s)' % (time.strftime(SHORT_TIME_FORMAT), day_shortname)
    text = u'•' + ' %s\n%s' % (time_str, doc['post'])
    return text


def archive(to_archive, pwd, location):
    subprocess.call(['7z', 'a', '-p%s' % pwd, '-y', location] + to_archive)


def history_cursor_to_str(cur):
    reprs = [get_text_repr(d) for d in cur]
    return '\n\n'.join(reprs[::-1])


def recent(bot, update):
    user = update.message.from_user
    user_collection = get_user_collection(user)

    msg = update.message.text.replace('/recent', '')
    find_tags = [t[1:] for t in HASHTAG_RE.findall(msg)]

    find = {}
    if find_tags:
        find['tags'] = {'$in': find_tags}
    elif msg.strip() == '?':
        find['tags'] = {'$size': 0}

    recent_cur = user_collection.find(find).sort('time', -1).limit(N_RECENT)
    recent_str = history_cursor_to_str(recent_cur)
    if not recent_str.strip():
        recent_str = EMPTY_MSG
    message = update.message.reply_text(recent_str, disable_web_page_preview=True)


def search(bot, update):
    user = update.message.from_user
    user_collection = get_user_collection(user)

    # make sure user collection has a text index
    user_collection.create_index([('post', TEXT)], default_language='english')

    msg = update.message.text.replace('/search', '')

    res_cur = user_collection.find({'$text': {'$search': msg }}) \
                             .sort('time', -1) \
                             .limit(N_RECENT)
    res_str = history_cursor_to_str(res_cur)
    if not res_str.strip():
        res_str = EMPTY_MSG
    message = update.message.reply_text(res_str, disable_web_page_preview=True)


def undo(bot, update):
    user = update.message.from_user
    user_collection = get_user_collection(user)

    last_added = user_collection.find({}).sort('_id', -1).next()
    text = get_text_repr(last_added)
    id_to_remove = last_added['_id']
    user_collection.remove(id_to_remove)
    update.message.reply_text(u'🗑\n\n' + text)


def get_first_hashtag(post):
    tags = HASHTAG_RE.findall(post)
    return tags[0] if tags else ''


def export(bot, update):
    user = update.message.from_user
    user_collection = get_user_collection(user)

    msg = update.message.text.replace('/export', '')
    find_tags = [t[1:] for t in re.findall(HASHTAG_RE, msg)]

    msg = HASHTAG_RE.sub('', msg)
    non_commands = [s for s in msg.strip().split(' ') if '/' not in s and s]
    if non_commands:
        password = non_commands[0]
    else:
        password = uuid.uuid4().hex[:16]

    find = {}
    if find_tags:
        find['tags'] = {'$in': find_tags}

    cur = user_collection.find(find).sort('time', -1)
    
    if not os.path.exists(settings.TEMP_DIR):
        os.makedirs(settings.TEMP_DIR)

    export_path = os.path.join(settings.TEMP_DIR, settings.EXPORT_FILENAME)
    with open(export_path, 'wb+') as f:
        writer = csv.writer(f, encoding='utf-8')
        writer.writerow(['Time', 'Tag', 'Record'])
        [writer.writerow([
                d['time'].strftime(LONG_TIME_FORMAT),
                get_first_hashtag(d['post']),
                d['post']
                ]) for d in cur]

    url = archive_and_host(export_path, password)

    chat_id = update.message.chat_id
    bot.send_document(chat_id, url)

    update.message.reply_text(u'\U0001F4E9' + ' password: `%s`' % password, 
                              parse_mode='Markdown')


def help(bot, update):
    update.message.reply_text(RULES, parse_mode='Markdown')


def get_document_from_message(msg):
    DATETIME_SET_RE = r'#t (\d{4}.\d{2}.\d{2} \d{1,2}:\d{1,2})'
    timestamp = re.search(DATETIME_SET_RE, msg)
    if timestamp:
        explicit_time = datetime.strptime(timestamp.group(1), SHORT_TIME_FORMAT)
        msg = re.sub(DATETIME_SET_RE, '', msg)
    else:
        explicit_time = None

    tags = [t[1:] for t in HASHTAG_RE.findall(msg)]
    post = msg

    doc = {
	'time': explicit_time or datetime.utcnow(),
        'post': post,
        'tags': tags,
    }
    return doc


def stats(bot, update):
    user = update.message.from_user
    user_coll = get_user_collection(user)
    response = '🗄 Your Daytobase has {} records\n'.format(user_coll.count())

    if user.id in settings.ADMIN_IDS:
        client = MongoClient()
        db = client['daytobase']
        coll_counts = [db[coll].count() for coll in db.collection_names()]
        response += '\nDaytobase has `{}` users\n'.format(len(coll_counts))
        response += 'Biggest collection sizes: `{}`\n'.format(sorted(coll_counts)[-3:])

        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_counts = [db[coll].find({'time': {'$gt': month_ago}}).count()
                         for coll in db.collection_names()]
        response += 'New records over past 30 days:  `{}`\n'.format(sum(recent_counts))
        active_colls = sum([c > 0 for c in recent_counts])
        response += 'Users active over past 30 days: `{}`\n'.format(active_colls)
    
    update.message.reply_text(response, parse_mode='Markdown')


def count(bot, update):
    user = update.message.from_user
    user_coll = get_user_collection(user)
    
    msg = update.message.text.replace('/export', '')
    find_tags = [t[1:] for t in re.findall(HASHTAG_RE, msg)]

    count_intervals = [
                ('last 7 days', {'$gt': datetime.utcnow() - timedelta(days=7)}),
                ('last 30 days', {'$gt': datetime.utcnow() - timedelta(days=30)}),
                ('previous 30 days', {
                    '$gt': datetime.utcnow() - timedelta(days=60),
                    '$lte': datetime.utcnow() - timedelta(days=30)
                    }
                )
            ]
    
    if find_tags:
        tag_list = ' or '.join(['*{}*'.format(t) for t in find_tags])
        count_summary = '🗄 tagged {}:\n'.format(tag_list)
    else:
        count_summary = '🗄 counts:\n'

    for interval_name, interval_condition in count_intervals:
        find_condition = {'tags': {'$in': find_tags}} if find_tags else {}
        find_condition['time'] = interval_condition
        count = user_coll.find(find_condition).count()
        count_summary += '- {}: {}\n'.format(interval_name, count)

    update.message.reply_text(count_summary, parse_mode='Markdown')
    

def pm(bot, update):
    msg = update.message.text
    user = update.message.from_user
    
    user_collection = get_user_collection(user)
    doc = get_document_from_message(msg)
    doc_id = user_collection.insert_one(doc)
    if doc_id:
        update.message.reply_text(POSTED_MSG)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(settings.BOT_ACCESS_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("recent", recent))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("undo", undo))
    dp.add_handler(CommandHandler("export", export))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("count", count))

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

