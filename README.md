# Youtube Videos Metadata & Comments Scraper
Python scripts to scrape the Metadata and comments for Youtube Videos.

## Functionalities:
1. Search top N results from a search query
2. Scrape comments from a given video id
3. Reply to specific comments
4. Fetch username(possibly same as emailid) of commenters

First of all, we need to have `DEVELOPER_KEY` of YoutubeDataAPI for this script to work. You can grab them <a href="https://console.developers.google.com" target="_blank">here</a>.

I am using an external library called `pafy` to download some data about Youtube. You can know more details about it <a href="https://pythonhosted.org/Pafy/" target="_blank">here</a>.

After successful scraping I am storing all those data into a CSV file. So I have imported  library called `csv`.

Now its time to do some scraping :

Import all required libraries into our file.

```python
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy
import csv
```

Now its time to add our developers key and build youtube.

```python
DEVELOPER_KEY = "#AddYourDeveloperKey"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
pafy.set_api_key("#AddYourAPIKey")

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
```

We will take the Youtube ID as input and make it into a Perfect Youtube URL.

```python
videoId = raw_input("ID of youtube video : \n")
url = "https://www.youtube.com/watch?v=" + videoId
```

Requesting Metadata from `pafy`

```python
video = pafy.new(url)
```

Its time to get all the comments from that Youtube Vdeoa dn save it into an array. Default max results you can get is 100. So if a Video has more than 100 comments we need to iterate the same function to get all the comments.

```python
results = youtube.commentThreads().list(
		    part="snippet",
		    maxResults=100,
		    videoId=videoId,
		    textFormat="plainText"
		  ).execute()
totalResults = 0
totalResults = int(results["pageInfo"]["totalResults"])
count = 0
nextPageToken = ''
comments = []
further = True
first = True
while further:
	halt = False
	if first == False:
		print "."
		try:
	  		results = youtube.commentThreads().list(
	  		  part="snippet",
	  		  maxResults=100,
	  		  videoId=videoId,
	  		  textFormat="plainText",
	  		  pageToken=nextPageToken
	  		).execute()
	  		totalResults = int(results["pageInfo"]["totalResults"])
	  	except HttpError, e:
			print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
			halt = True
	if halt == False:
	  	count += totalResults
	  	for item in results["items"]:
		  	comment = item["snippet"]["topLevelComment"]
		  	author = comment["snippet"]["authorDisplayName"]
		  	text = comment["snippet"]["textDisplay"]
		  	comments.append([author,text])
		if totalResults < 100:
			further = False
			first = False
		else:
			further = True
			first = False
			try:
				nextPageToken = results["nextPageToken"]
			except KeyError, e:
				print "An KeyError error occurred: %s" % (e)
				further = False
```

Now its time to add all the data  to our csv file.

```python
add_data(videoId,video.title,video.description,video.author,video.published,video.viewcount, video.duration, video.likes, video.dislikes,video.rating,video.category,comments)
```

Following code is used to add our data into a csv file.

```python
def add_data(vID,title,description,author,published,viewcount, duration, likes, dislikes,rating,category,comments):
	data = [vID,title,description,author,published,viewcount, duration, likes, dislikes,rating,category,comments]
	with open("scraper.csv", "a") as fp:
	    wr = csv.writer(fp, dialect='excel')
	    wr.writerow(data)
```

This way we can get all the data and comments of a youtube video.

Now a simple extension of this script is to get all the data of top 10 search results.

For this I take the search term as input and then called YoutubeAPI for the search results. From that results I would just take the top 10 videoIDS and call the above script to get all required data.

```python
searchTerm = raw_input("Term you want to Search : \n")
search_response = youtube.search().list(
      q=searchTerm,
      part="id,snippet",
      maxResults=30
    ).execute()
count = 0
for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      	if count <10:
	        vID = search_result["id"]["videoId"]
	        get_data(vID)
	        count += 1
	    else:
	    	break
    else:
    	continue
```


You can checkout the full scripts in this repo [here](https://github.com/Sunil02324/Youtube-Meta-Data-Comments-Scraper). Fork it or Star if you like it. 

You can mail me at <a href="mailto:sunil@suniltatipelly.in">sunil@suniltatipelly.in</a> for any queries or doubts regarding this.

### Support:

If you want the good work to continue please support us on

* [PAYPAL](https://www.paypal.me/ishandutta2007)
* [BITCOIN ADDRESS: 3LZazKXG18Hxa3LLNAeKYZNtLzCxpv1LyD](https://www.coinbase.com/join/5a8e4a045b02c403bc3a9c0c)
