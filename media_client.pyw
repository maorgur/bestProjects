import os
from dotenv import load_dotenv

load_dotenv()

import time

import httpx
from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
import asyncio

SERVER_URL = os.getenv("SERVER_URL", "http://localhost/AOD/post/media")
SECRET = int(os.getenv("SECRET_KEY", 0))
HEARTBEAT_INTERVAL = 500

async def get_media_info():
    # Get the session manager
    sessions = await MediaManager.request_async()

    current_session = sessions.get_current_session()
    if not current_session:
        print("No media session active")
        return None, None

    # Get playback info
    media_properties = await current_session.try_get_media_properties_async()
    playback_info = current_session.get_playback_info()

    if playback_info.playback_status != 4: #Playing
        return None, None
    title = media_properties.title
    artist = media_properties.artist
    if (title and "-" in title):
        title = title.split("-")[0]
    if (artist and "-" in artist):
        artist = artist.split("-")[0]
    title = title.strip() if title else None
    artist = artist.strip() if artist else None

    return title, artist

async def main():
    last_title = None
    last_artist = None
    last_update_timestamp = time.time()

    while True:
        title, artist = await get_media_info()
        if (title != last_title or artist != last_artist) or time.time() - last_update_timestamp > HEARTBEAT_INTERVAL:
            last_title = title
            last_artist = artist
            last_update_timestamp = time.time()
            print(f"Now playing: {artist} - {title}")

            with httpx.Client() as client:
                try:
                    response = client.post(SERVER_URL, json={"secret": SECRET, "artist": artist, "title": title}, timeout=2)
                    if response.status_code//100 >= 4:
                        await asyncio.sleep(10) #wait more if server down
                        title, artist = None, None #to ask again next time
                except httpx.RequestError as e:
                    print(f"Failed to send media info: {e}")
                    await asyncio.sleep(10) #wait more if server down
                    title, artist = None, None #to ask again next time
    
        await asyncio.sleep(2)


asyncio.run(main())
