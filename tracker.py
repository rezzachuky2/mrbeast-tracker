import os
import requests

CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

LAST_VIDEO_FILE = "last_video.txt"


# =============================
# GET UPLOADS PLAYLIST ID
# =============================

def get_uploads_playlist():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    )

    data = requests.get(url).json()
    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


# =============================
# GET LATEST VIDEO FROM PLAYLIST
# =============================

def get_latest_video(playlist_id):
    url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&playlistId={playlist_id}&maxResults=1&key={YOUTUBE_API_KEY}"
    )

    data = requests.get(url).json()

    item = data["items"][0]
    video_id = item["snippet"]["resourceId"]["videoId"]
    title = item["snippet"]["title"]
    published = item["snippet"]["publishedAt"]
    thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

    return video_id, title, published, thumbnail


# =============================
# TELEGRAM SEND
# =============================

def send_new_video_alert(title, video_id, thumbnail):
    video_url = f"https://youtu.be/{video_id}"

    message = f"""
🔥 *MRBEAST UPLOADED NEW VIDEO!*

📺 *Title:* {title}
🔗 {video_url}
"""

    # Send thumbnail + caption
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "caption": message,
            "parse_mode": "Markdown"
        },
        files={"photo": requests.get(thumbnail).content}
    )


# =============================
# MAIN
# =============================

def main():
    playlist_id = get_uploads_playlist()
    video_id, title, published, thumbnail = get_latest_video(playlist_id)

    # Check if new video
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE) as f:
            last_video = f.read().strip()

        if last_video == video_id:
            print("No new video.")
            return

    # New video detected
    print("New video found:", title)

    send_new_video_alert(title, video_id, thumbnail)

    with open(LAST_VIDEO_FILE, "w") as f:
        f.write(video_id)


if __name__ == "__main__":
    main()
