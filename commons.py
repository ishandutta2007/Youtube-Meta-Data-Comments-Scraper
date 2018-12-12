from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv
from datetime import date, datetime, timedelta
import traceback

import pprint as pp
import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import constants

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, \
    UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support.select import Select
import time

def selenium_authorise(auth_url):
    try:
        print('Authorising via Selenium Launched')
        chrome_options = Options()
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-plugins-discovery")
        # chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=constants.CHROME_DRIVER_PATH)
        driver.get(auth_url)

        time.sleep(2)
        goog_email_element = driver.find_element_by_id("identifierId")
        goog_email_element.send_keys(constants.GOOG_ID)
        goog_email_element.send_keys(Keys.ENTER)
        time.sleep(2)
        goog_pass_element = driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
        goog_pass_element.send_keys(constants.GOOG_PASS)
        goog_pass_element.send_keys(Keys.ENTER)
        print('Authorising via Selenium. Loggingin...')
        time.sleep(5)

        allow_button = driver.find_element_by_id('submit_approve_access')
        allow_button.click()
        print('Authorising via Selenium. Submitting Approval...')
        time.sleep(10)

        code_input = driver.find_element_by_id('code')
        code_value = code_input.get_attribute('value')
        print('Authorising via Selenium. Fetched authorization code:', code_value)
        time.sleep(5)
        driver.quit()
        return code_value
    except Exception:
        traceback.print_exc()
        driver.quit()

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(constants.CLIENT_SECRETS_FILE, constants.SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    auth_url, _ = flow.authorization_url(prompt='consent')
    code = selenium_authorise(auth_url)
    flow.fetch_token(code=code)
    return build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION, credentials = flow.credentials)

def fetch_results(youtube, next_page_token, video_id):
    results = youtube.commentThreads().list(
                part="snippet",
                maxResults=100,
                videoId=video_id,
                textFormat="plainText",
                pageToken=next_page_token
            ).execute()
    total_results = int(results["pageInfo"]["totalResults"])
    return total_results, results

def print_response(response):
    print(response)

def build_resource(properties):
    resource = {}
    for p in properties:
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                ref[key] = {}
                ref = ref[key]
            else:
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

def channels_list_by_id(youtube, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)

    response = youtube.channels().list(
    **kwargs
    ).execute()

    return response

def retrieve_username(youtube, item):
    response = channels_list_by_id(youtube,
        part='snippet',
        id = item["snippet"]["topLevelComment"]['snippet']['authorChannelId']['value'])

    try:
        customUrl = response['items'][0]['snippet']['customUrl']
        with open("username.csv", "a") as fp:
            fp.write(customUrl + '\n')
        print('customUrl', customUrl)
    except Exception:

def process_and_print_comment(len_comments, item):
    comment = item["snippet"]["topLevelComment"]
    comment_id = item['id']
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    # print_comment(len_comments, author, datetime.now() - datetime.strptime(comment["snippet"]["publishedAt"],"%Y-%m-%dT%H:%M:%S.000Z"), text)
    return comment_id, author, text

def scrape_metadata(video_id):
    url = "https://www.youtube.com/watch?v=" + video_id
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
    return video

def add_data_to_csv(video_id, title, description, author, published, viewcount, duration, likes, dislikes, rating, category, comments):
    data = [video_id, title, description, author, published, viewcount, duration, likes, dislikes, rating, category, comments]
    with open("scraper.csv", "a") as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(data)

def reply_to_comment(client, comment_id, text):
    if text.find('congratulations')>=0 or text.find('congrats')>=0:
        comments_insert(client,
            {'snippet.parentId': comment_id,
            'snippet.textOriginal': "Thank you"},
            part='snippet')

def scrape_comments_and_reply(client, youtube, video_id, max_comment_fetch_limit=10000, is_reply = True):
    count = 0
    comments = []
    next_page_token = ''
    while True:
        try:
            total_results, results = fetch_results(youtube, next_page_token, video_id)
            count += total_results
            for item in results["items"]:
                comment_id, author, text = process_and_print_comment(len(comments), item)

                retrieve_username(youtube, item)

                if is_reply:
                    reply_to_comment(client, comment_id, text)
                comments.append([author, text])

            print("fetched %d more comments, total comments count: %d" % (total_results, count))
            if count > max_comment_fetch_limit:
                print('MAx comment fetch limit reached, exiting loop')
                break
            next_page_token = results["nextPageToken"]
        except HttpError as e:
            print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))
            traceback.print_exc()
        except KeyError as e:
            print(("An KeyError error occurred: %s" % (e)))
            print('Last page reached, exiting loop')
            break
    return comments
