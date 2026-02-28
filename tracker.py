import os
import requests
from PIL import Image, ImageDraw, ImageFont

CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

LAST_SUB_FILE = "last_sub.txt"
LAST_VIDEO_FILE = "last_video.txt"


# =============================
# API CALLS
# =============================

def get_subscriber():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    )
    data = requests.get(url).json()
    return int(data["items"][0]["statistics"]["subscriberCount"])


def get_latest_video():
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&channelId={CHANNEL_ID}&order=date&maxResults=1&type=video&key={YOUTUBE_API_KEY}"
    )
    data = requests.get(url).json()
    video_id = data["items"][0]["id"]["videoId"]
    title = data["items"][0]["snippet"]["title"]
    return video_id, title


# =============================
# IMAGE GENERATOR
# =============================

def generate_image(subs, title):
    formatted = f"{subs:,}"

    img = Image.open("background.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # Title small text
    small_font = ImageFont.truetype("font.otf", 40)
    draw.text((width/2, 80),
              "MRBEAST LIVE STATS",
              font=small_font,
              fill="white",
              anchor="mm")

    # Big subscriber text
    font_size = 180
    while font_size > 20:
        font = ImageFont.truetype("font.otf", font_size)
        bbox = draw.textbbox((0, 0), formatted, font=font)
        if bbox[2] - bbox[0] <= width * 0.8:
            break
        font_size -= 5

    draw.text((width/2, height/2),
              formatted,
              font=font,
              fill="white",
              anchor="mm")

    # Latest video title (cut if too long)
    title = title[:40] + "..." if len(title) > 40 else title
    draw.text((width/2, height - 60),
              f"Latest: {title}",
              font=small_font,
              fill="white",
              anchor="mm")

    img.save("output.png")


# =============================
# TELEGRAM
# =============================

def send_photo(caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open("output.png", "rb") as photo:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo},
        )


def send_text(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
    )


# =============================
# MAIN
# =============================

def main():
    subs = get_subscriber()
    video_id, title = get_latest_video()

    new_sub = False
    new_video = False

    # Check subscriber
    if os.path.exists(LAST_SUB_FILE):
        with open(LAST_SUB_FILE) as f:
            if int(f.read()) != subs:
                new_sub = True
    else:
        new_sub = True

    # Check video
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE) as f:
            if f.read() != video_id:
                new_video = True
    else:
        new_video = True

    if new_sub or new_video:
        generate_image(subs, title)

        if new_video:
            send_text("🔥 MRBEAST UPLOADED NEW VIDEO!")
        send_photo(caption="Live Update")

        with open(LAST_SUB_FILE, "w") as f:
            f.write(str(subs))

        with open(LAST_VIDEO_FILE, "w") as f:
            f.write(video_id)


if __name__ == "__main__":
    main()
