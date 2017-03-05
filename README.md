# Daytobase

Notes are not documents, they are *messages*.

Daytobase is a [Telegram](https://telegram.org/) bot that records whatever you send it to a database. You can review records by hashtags, search by text and export them to CSV. Try it [here](https://telegram.me/daytobasebot)!

## Software requirements

1. MongoDB instance running on the same machine as the bot
2. A static file server (like [nginx](https://www.nginx.com)) to serve your data exports
3. `7z` to encrypt your data exports (`pip install p7zip-full`) 

## Python packages

1. Amazing [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library (5.2.0)
2. [PyMongo](https://pypi.python.org/pypi/pymongo) (3.4.0)
3. [UnicodeCSV](https://pypi.python.org/pypi/unicodecsv/0.14.1) (0.14.1)

