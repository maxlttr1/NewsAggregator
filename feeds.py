import feedparser

YTB_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id="

def get_latest_video(channel_id):
    feed = feedparser.parse(YTB_RSS + channel_id)
    if not feed.entries:
        return None
    
    return {
        "title": feed.entries[0].title,
        "link": feed.entries[0].link,
        "channel": feed.feed.title
    }
