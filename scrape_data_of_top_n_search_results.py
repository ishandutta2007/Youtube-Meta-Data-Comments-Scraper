from apiclient.discovery import build
# from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv

import sys
import imp

import constants
pafy.set_api_key(constants.DEVELOPER_KEY)
from commons import fetch_results, scrape_metadata, scrape_comments, add_data_to_csv

youtube = build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION,developerKey=constants.DEVELOPER_KEY)

def get_data(video_id):
    print("\n\nScraping videoId %s" % video_id)
    video = scrape_metadata(video_id)
    comments = scrape_comments(video_id)
    add_data_to_csv(video_id, video.title, video.description, video.author, video.published, video.viewcount, video.duration, video.likes, video.dislikes, video.rating, video.category, comments)

if __name__ == '__main__':
    search_term = eval(input("Term you want to Search : \n"))
    no_of_res = eval(input("Number of videos you would want to scrape: \n"))
    search_response = youtube.search().list(
        q=search_term,
        part="id,snippet",
        maxResults=30
        ).execute()
    only_videos = [x for x in search_response.get("items", []) if x["id"]["kind"]=='youtube#video'][:no_of_res]
    for search_result in only_videos:
        video_id = search_result["id"]["videoId"]
        get_data(video_id)
