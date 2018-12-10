from apiclient.discovery import build
# from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv
from datetime import date, datetime, timedelta
import sys
import imp
import os
import traceback

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from commons import fetch_results, scrape_metadata, scrape_comments, add_data_to_csv
import constants
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

pafy.set_api_key(constants.DEVELOPER_KEY)
# youtube = build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION, developerKey=constants.DEVELOPER_KEY)

if __name__ == '__main__':
    video_id = eval(input("ID of youtube video : \n"))
    video = scrape_metadata(video_id)
    comments = scrape_comments(video_id)
    add_data_to_csv(video_id, video.title, video.description, video.author, video.published, video.viewcount, video.duration, video.likes, video.dislikes, video.rating, video.category, comments)
