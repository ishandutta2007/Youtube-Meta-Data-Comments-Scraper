from apiclient.discovery import build
# from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv
import os
from datetime import date, datetime, timedelta
import traceback

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from commons import get_authenticated_service, fetch_results, scrape_metadata, scrape_comments_and_reply, add_data_to_csv
import constants
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

pafy.set_api_key(constants.DEVELOPER_KEY)

if __name__ == '__main__':
    client = get_authenticated_service()
    youtube = build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION, developerKey=constants.DEVELOPER_KEY)
    video_id = eval(input("ID of youtube video : \n"))
    video = scrape_metadata(video_id)
    comments = scrape_comments_and_reply(client, youtube, video_id)
    add_data_to_csv(video_id, video.title, video.description, video.author, video.published, video.viewcount, video.duration, video.likes, video.dislikes, video.rating, video.category, comments)
