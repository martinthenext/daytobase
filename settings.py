impot os
# Your Telegram bot access key
BOT_ACCESS_KEY = os.environ['BOT_ACCESS_KEY']

# Temporary dir for exports. Ideally you would clean up once in a while
TEMP_DIR = '/tmp'
# Filename for exports
EXPORT_FILENAME = 'daytobase.csv'

# External web server setup
# A directory on your server that serves static content
STATIC_DIR = '/var/www/daytobase'
# A URL at which this static content is served
STATIC_URL = r'http://localhost/daytobase'

# Admin user ids to access usage statistics
ADMIN_IDS = []
