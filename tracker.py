import os
import requests
from PIL import Image, ImageDraw, ImageFont

# ===== CONFIG =====
CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_FILE = "last.txt"

# ===== GET SUBSCRIBER =====
def get_subscriber():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return int(r["items"][0]["statistics"]["subscriberCount"])

# ===== GENERATE IMAGE =====
def generate_image(subs):
    formatted = f"{subs:,}"

    img = Image.open("background.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    width, height = img.size

    max_width = width * 0.75
    font_size = 200

    while True:
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

# ===== SEND TO TELEGRAM =====
def send_telegram():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open("output.png", "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})

# ===== CHECK DUPLICATE =====
def main():
    subs = get_subscriber()

    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r") as f:
            last = int(f.read())
        if subs == last:
            print("No change.")
            return

    generate_image(subs)
    send_telegram()

    with open(LAST_FILE, "w") as f:
        f.write(str(subs))

if __name__ == "__main__":
    main()
