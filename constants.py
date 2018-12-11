import os
import configparser
config = configparser.ConfigParser()
config.read("config.txt")

DEVELOPER_KEY = config.get("configuration", "goog_ishandutta2007_apikey")

GOOG_ID = 'ishandutta2007'
GOOG_PASS = config.get("configuration", "goog_ishandutta2007_password")

CLIENT_SECRETS_FILE = "client_secret_ishandutta2007.json"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

CHROME_DRIVER_PATH = '/Users/ishandutta2007/Documents/Projects/chromium/chromium/src/out/Default/chromedriver_gleam'
