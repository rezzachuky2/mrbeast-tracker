import os
import requests
from PIL import Image, ImageDraw, ImageFont

# =============================
# CONFIG
# =============================

CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

LAST_FILE = "last.txt"


# =============================
# GET SUBSCRIBER
# =============================

def get_subscriber():
    if not YOUTUBE_API_KEY:
        raise Exception("YOUTUBE_API_KEY not loaded")

    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    )

    r = requests.get(url, timeout=15)
    data = r.json()

    if "error" in data:
        raise Exception(f"YouTube API Error: {data}")

    if "items" not in data or not data["items"]:
        raise Exception(f"Invalid API response: {data}")

    return int(data["items"][0]["statistics"]["subscriberCount"])


# =============================
# GENERATE IMAGE
# =============================

def generate_image(subs):
    formatted = f"{subs:,}"

    img = Image.open("background.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    width, height = img.size
    max_width = width * 0.75

    font_size = 200

    while font_size > 10:
        font = ImageFont.truetype("font.otf", font_size)
        bbox = draw.textbbox((0, 0), formatted, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            break

        font_size -= 5

    x = width / 2
    y = height / 2

    # Shadow
    draw.text((x+3, y+3), formatted, font=font, fill="black", anchor="mm")
    draw.text((x, y), formatted, font=font, fill="white", anchor="mm")

    img.save("output.png")


# =============================
# SEND TELEGRAM
# =============================

def send_telegram():
    if not BOT_TOKEN or not CHAT_ID:
        raise Exception("Telegram secrets not loaded")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open("output.png", "rb") as photo:
        r = requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"photo": photo},
            timeout=20,
        )

    if r.status_code != 200:
        raise Exception(f"Telegram error: {r.text}")


# =============================
# MAIN
# =============================

def main():
    try:
        subs = get_subscriber()
        print("Subscriber:", subs)

        if os.path.exists(LAST_FILE):
            with open(LAST_FILE, "r") as f:
                last = int(f.read())

            if subs == last:
                print("No change. Skip.")
                return

        generate_image(subs)
        send_telegram()

        with open(LAST_FILE, "w") as f:
            f.write(str(subs))

        print("Update sent.")

    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
