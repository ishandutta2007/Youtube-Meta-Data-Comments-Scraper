from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv
from datetime import date, datetime, timedelta
import sys
import imp
# imp.reload(sys)
# sys.setdefaultencoding('utf8')  
import os
import traceback

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import constants
pafy.set_api_key(constants.DEVELOPER_KEY)

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(constants.CLIENT_SECRETS_FILE, constants.SCOPES)
    credentials = flow.run_console()
    return build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION, credentials = credentials)

def print_response(response):
    print(response)

def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource

def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs

def comments_insert(client, properties, **kwargs):
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.comments().insert(
        body=resource,
        **kwargs
        ).execute()
    return print_response(response)

def print_comment(len_comments, author, delta, text):
    if delta.days > 365:
        print(len_comments  , author, str(int(delta.days/365))+ " years ago", text)
    elif delta.days > 30:
        print(len_comments  , author, str(int(delta.days/30))+ " months ago", text)
    elif delta.days > 7:
        print(len_comments  , author, str(int(delta.days/7))+ " weeks ago", text)
    elif delta.days > 0:
        print(len_comments  , author, str(int(delta.days))+ " days ago", text)
    elif delta.seconds > 3600:
        print(len_comments  , author, str(int(delta.seconds/3600))+ " hours ago", text)
    elif delta.seconds > 60:
        print(len_comments  , author, str(int(delta.seconds/60))+ " minutes ago", text)
    else:
        print(len_comments  , author, str(delta.seconds)+ " seconds ago", text)

def process_and_print_comment(len_comments, item):
    comment = item["snippet"]["topLevelComment"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    # print_comment(len_comments, author, datetime.now() - datetime.strptime(comment["snippet"]["publishedAt"],"%Y-%m-%dT%H:%M:%S.000Z"), text)
    return author, text

def fetch_results(nextPageToken):
    results = youtube.commentThreads().list(
                part="snippet",
                maxResults=100,
                videoId=videoId,
                textFormat="plainText",
                pageToken=nextPageToken
            ).execute()
    totalResults = int(results["pageInfo"]["totalResults"])
    return totalResults, results

def add_data_to_csv(vID,title,description,author,published,viewcount, duration, likes, dislikes,rating,category,comments):
    data = [vID,title,description,author,published,viewcount, duration, likes, dislikes,rating,category,comments]
    with open("scraper.csv", "a") as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(data)

def scrape_metadata(videoId):
    url = "https://www.youtube.com/watch?v=" + videoId
    video = pafy.new(url)
    print('video.title:', video.title)
    print('video.rating:', video.rating)
    print('video.viewcount:', video.viewcount)
    print('video.author:', video.author)
    print('video.length:', video.length)
    print('video.duration:', video.duration)
    print('video.likes:', video.likes)
    print('video.dislikes:', video.dislikes)
    print('video.description:', video.description)
    add_data_to_csv(videoId,video.title,video.description,video.author,video.published,video.viewcount, video.duration, video.likes, video.dislikes,video.rating,video.category,comments)

def scrape_comments(videoId):
    count = 0
    comments = []
    next_page_token = ''
    while True:
        try:
            totalResults, results = fetch_results(next_page_token)

            count += totalResults
            for item in results["items"]:
                author, text = process_and_print_comment(len(comments), item)
                comments.append([author, text])

            print("fetched %d more, total count: %d" % (totalResults, count))
            next_page_token = results["nextPageToken"]
        except HttpError as e:
            print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))
            traceback.print_exc()
        except KeyError as e:
            print(("An KeyError error occurred: %s" % (e)))
            print('possibly last page reached, ie results["nextPageToken"] not found')
            traceback.print_exc()
            break
    print(comments)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    client = get_authenticated_service()
    youtube = build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION, developerKey=constants.DEVELOPER_KEY)
    videoId = eval(input("ID of youtube video : \n"))
    scrape_metadata(videoId)
    scrape_comments(videoId)
