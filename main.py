import schedule
import time
import requests
import feedparser
import yaml

def read_yaml(file="data.yaml"):
    f = open(file)
    data = yaml.safe_load(f)
    return data

ytbRSS = "https://www.youtube.com/feeds/videos.xml?channel_id="

def convert_ytb_ids(ytbChannels):
    return [ytbRSS + channel for channel in ytbChannels]

def get_latest_video(ytbChannelURL):
    feed = feedparser.parse(ytbChannelURL)
    if not feed.entries:
        return None
    return({
        "title": feed.feed.title,
        "link": feed.entries[0].link
    })


def discordNotif(webhookUrl, data):
    data = {
        "content": str(data["link"])
    }
    response = requests.post(webhookUrl, json=data)
    if response.status_code == 204:
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message: {response.status_code}, {response.text}")

def main():
    data = read_yaml()
    print(data)
    ytbChannelsURL = convert_ytb_ids(data["channelsIDs"])
    last_seen = {URL: None for URL in ytbChannelsURL}
    discordWebhookUrl = data["discordWebhookUrl"]

    while True:
        for URL in ytbChannelsURL:
            video = get_latest_video(URL)
            if video is None:
                print("Didn't find any video")
                continue
            if last_seen[URL] != video["link"]:
                last_seen[URL] = video["link"]
                discordNotif(discordWebhookUrl, video)
        time.sleep(120)

if __name__ == "__main__":
    main()