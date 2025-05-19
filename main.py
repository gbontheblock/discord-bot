import os
import discord
import asyncio
from googleapiclient.discovery import build

DISCORD_CHANNEL_ID = 1050628641261879376
YOUTUBE_CHANNEL_IDS = [
    "UCzceiC2snNLjczGA-qOYXfw",
    "UCo2E__x4A6xSaQAat53-F4A"
]

DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

last_video_ids = {}

async def check_new_videos():
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print("Discord channel not found")
        return

    while not client.is_closed():
        for yt_channel_id in YOUTUBE_CHANNEL_IDS:
            request = youtube.activities().list(
                part="contentDetails",
                channelId=yt_channel_id,
                maxResults=1
            )
            response = request.execute()

            items = response.get("items", [])
            if not items:
                continue

            latest_video_id = None
            if 'upload' in items[0]['contentDetails']:
                latest_video_id = items[0]['contentDetails']['upload']['videoId']
            elif 'video' in items[0]['contentDetails']:
                latest_video_id = items[0]['contentDetails']['video']['videoId']

            if latest_video_id is None:
                continue

            if last_video_ids.get(yt_channel_id) == latest_video_id:
                continue

            video_request = youtube.videos().list(
                part="contentDetails,snippet",
                id=latest_video_id
            )
            video_response = video_request.execute()
            video_items = video_response.get("items", [])
            if not video_items:
                continue

            video = video_items[0]
            duration_iso = video['contentDetails']['duration']
            title = video['snippet']['title']
            url = f"https://www.youtube.com/watch?v={latest_video_id}"

            duration_seconds = parse_iso8601_duration(duration_iso)

            if duration_seconds > 60:
                msg = f"New video: {title}\nhttps://youtu.be/{video_id}"

Duration: {duration_seconds} seconds"
                await channel.send(msg)

                last_video_ids[yt_channel_id] = latest_video_id

        await asyncio.sleep(300)

def parse_iso8601_duration(duration):
    import re
    pattern = re.compile(
        'PT'
        '(?:(\d+)H)?'
        '(?:(\d+)M)?'
        '(?:(\d+)S)?'
    )
    match = pattern.match(duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(check_new_videos())

client.run(DISCORD_BOT_TOKEN)
