import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

LAST_SUB_FILE = "last_sub.txt"
LAST_VIDEO_FILE = "last_video.txt"


def safe_request(url):
    try:
        r = requests.get(url, timeout=15)
        return r.json()
    except:
        return None


def get_channel_data():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=statistics,contentDetails&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    )
    data = safe_request(url)
    if not data or "items" not in data:
        return None

    item = data["items"][0]
    subs = int(item["statistics"]["subscriberCount"])
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    return subs, uploads


def get_latest_video(playlist_id):
    url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&playlistId={playlist_id}&maxResults=1&key={YOUTUBE_API_KEY}"
    )
    data = safe_request(url)
    if not data or "items" not in data:
        return None

    item = data["items"][0]
    return (
        item["snippet"]["resourceId"]["videoId"],
        item["snippet"]["title"],
        item["snippet"]["thumbnails"]["high"]["url"],
    )


def generate_banner(subs):
    formatted = f"{subs:,}"

    img = Image.new("RGB", (1000, 500), "#111827")
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype("font.otf", 50)
    big_font = ImageFont.truetype("font.otf", 160)
    small_font = ImageFont.truetype("font.otf", 30)

    draw.text((500, 80), "MRBEAST LIVE COUNT", font=title_font, fill="white", anchor="mm")

    draw.text((500, 250), formatted, font=big_font, fill="#22d3ee", anchor="mm")

    draw.text((500, 440),
              f"Updated {datetime.utcnow().strftime('%H:%M UTC')}",
              font=small_font,
              fill="gray",
              anchor="mm")

    img.save("output.png")


def send_photo(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(file_path, "rb") as photo:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo},
        )


def send_new_video(title, video_id, thumbnail):
    message = f"""🔥 *NEW MRBEAST VIDEO!*

📺 *{title}*
🔗 https://youtu.be/{video_id}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    requests.post(
        url,
        data={"chat_id": CHAT_ID, "caption": message, "parse_mode": "Markdown"},
        files={"photo": requests.get(thumbnail).content},
    )


def main():
    channel_data = get_channel_data()
    if not channel_data:
        print("API error")
        return

    subs, uploads = channel_data
    latest = get_latest_video(uploads)
    if not latest:
        return

    video_id, title, thumbnail = latest

    # ===== CHECK VIDEO =====
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE) as f:
            if f.read() != video_id:
                send_new_video(title, video_id, thumbnail)
                with open(LAST_VIDEO_FILE, "w") as w:
                    w.write(video_id)
    else:
        with open(LAST_VIDEO_FILE, "w") as w:
            w.write(video_id)

    # ===== CHECK SUBSCRIBER =====
    if os.path.exists(LAST_SUB_FILE):
        with open(LAST_SUB_FILE) as f:
            if int(f.read()) != subs:
                generate_banner(subs)
                send_photo("output.png", "Live Subscriber Update")
                with open(LAST_SUB_FILE, "w") as w:
                    w.write(str(subs))
    else:
        with open(LAST_SUB_FILE, "w") as w:
            w.write(str(subs))


if __name__ == "__main__":
    main()
