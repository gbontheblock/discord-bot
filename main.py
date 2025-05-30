import os
import discord
import asyncio
from discord.ext import tasks
from googleapiclient.discovery import build
import threading
from flask import Flask  # <-- Make sure to import Flask

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_IDS = [
    "UCzceiC2snNLjczGA-qOYXfw",  # normal channel
    "UCo2E__x4A6xSaQAat53-F4A"   # plus channel
]
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
last_video_ids = {}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_new_videos.start()

@tasks.loop(minutes=1)
async def check_new_videos():
    for channel_id in YOUTUBE_CHANNEL_IDS:
        request = youtube.activities().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=1
        )
        response = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            continue

        latest_video = response["items"][0]
        if latest_video["snippet"]["type"] != "upload":
            continue

        video_id = latest_video["contentDetails"]["upload"]["videoId"]
        title = latest_video["snippet"]["title"]

        if channel_id not in last_video_ids or last_video_ids[channel_id] != video_id:
            last_video_ids[channel_id] = video_id
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                msg = f"New video: **{title}**\nhttps://youtu.be/{video_id}"
                await channel.send(msg)

# Flask server to keep Render happy
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Run Flask in a separate thread so it doesn't block your bot
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Run the Discord bot (this blocks the main thread)
client.run(DISCORD_TOKEN)
