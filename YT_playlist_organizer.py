from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
from datetime import timedelta

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Watch Later").sheet1

api_key = "AIzaSyBdxMg63PTs2PRIKEh-MnznwFQ3RX-ofr8"

youtube = build('youtube', 'v3', developerKey = api_key)

vid_ids = []
vid_titles = []
vid_channel = []
vid_durations = []
vid_seconds = []

nextPageToken = None

# pl_request = youtube.playlists().list(
# part = 'contentDetails, snippet',
# channelId = 'UCa5143fVsOtaLriJZDkw10w',
# )

# pl_response = pl_request.execute()

# for item in pl_response['items']:
#     print(item)
#     print()


while True:

    pl_request = youtube.playlistItems().list(
    part = 'contentDetails, snippet',
    playlistId = 'PLvQh1SvRh2sGJEJUmeZUIQd5tEUXQIehY',
    maxResults = 50,
    pageToken = nextPageToken
    )

    pl_response = pl_request.execute()

    for item in pl_response['items']:
        vid_ids.append(item['contentDetails']['videoId'])
        vid_titles.append(item['snippet']['title'])
        vid_channel.append(item['snippet']['videoOwnerChannelTitle'])

    vid_request = youtube.videos().list(
    part = 'contentDetails',
    id = ','.join(vid_ids)
    )

    vid_response = vid_request.execute()

    for item in vid_response['items']:
        duration = item['contentDetails']['duration']
        vid_durations.append(duration.strip("PT"))

    for duration in vid_durations:

        #Converting the format of _H_M_S to separate variables of hours, minutes and seconds
        
        try:
            hms_list = duration.split("H")
            x = hms_list[1].split("M")
            y = x[1].split("S")
            hms_list[1] = x[0]
            hms_list.append(y[0])

            hours = hms_list[0]
            minutes = hms_list[1]
            seconds = hms_list[2]

        except:

            try:
                hms_list = duration.split("M")
                hms_list[1] = hms_list[1].strip("S")

                hours = 0
                minutes = hms_list[0]
                seconds = hms_list[1]

            except:
                duration = duration.strip("S")

                hours = 0
                minutes = 0
                seconds = duration

        if hours == '':
            hours = 0
        if minutes == '':
            minutes = 0
        if seconds == '':
            seconds = 0

        try:
            totalSeconds = timedelta(
                hours = float(hours),
                minutes = float(minutes),
                seconds = float(seconds)
            ).total_seconds()
        except:
            totalSeconds = 0
            continue

        vid_seconds.append(totalSeconds)

    for i in range(len(vid_ids)):
        try:
            link = "https://www.youtube.com/watch?v=" + vid_ids[i]
            insertRow = [vid_titles[i], vid_channel[i], vid_durations[i], link, vid_seconds[i]]
            sheet.insert_row(insertRow, 2)
        except Exception as e:
            print(e)
            sleep(60)
            continue

    nextPageToken = pl_response.get('nextPageToken')

    if nextPageToken is None:
        break
