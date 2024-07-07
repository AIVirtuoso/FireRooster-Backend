import datetime
import io
import os
from pprint import pprint
from random import sample
import logging as log
import asyncio

import librosa
import requests
from pydub import AudioSegment
from app.Utils.remove_space import process_audio
from concurrent.futures import ThreadPoolExecutor

TEMP_FOLDER = "audios"

def format_datetime_for_url(date=None):
    # parse input date, for Url
    if date is None:
        date = datetime.datetime.now().date()

    datetime_obj = datetime.datetime(date.year, date.month, date.day)

    formatted_date = date.strftime("%m/%d/%Y")
    timestamp = int(datetime_obj.timestamp())

    return formatted_date, timestamp


def get_first_element(list):
    first_elem = list["data"][0] if list["data"] else None
    return first_elem


def extract_ids_from_archive(archive):
    return [{"id": item[0], "start_time": item[1], "end_time": item[2]} for item in archive["data"]] if "data" in archive else None


async def get_full_day_archives(session, feedId, date=None):
    # default to yesterday
    if date is None:
        date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    feed_archive_url = "https://www.broadcastify.com/archives/ajax.php"
    url_date = format_datetime_for_url(date)
    formatted_url = (
        f"{feed_archive_url}?feedId={feedId}&date={url_date[0]}&_={url_date[1]}"
    )
    print("formatted_url: ", formatted_url)
    feed_archive = session.get(formatted_url).json()
    audio_list = extract_ids_from_archive(feed_archive)
    return audio_list


async def save_and_convert_to_wav(file_stream, file_name):
    # download the file as mp3, then convers to wav
    file_stream.seek(0)

    print("file_name: ", file_name)
    
    file_path = os.path.join(TEMP_FOLDER, file_name + '_p.mp3')
    
    if os.path.exists(file_path):
        print("yes")
        return file_path
    else:
        pass

    with open(file_name + ".mp3", "wb") as file:
        file.write(file_stream.read())

    # convert MP3 to WAV
    audio = AudioSegment.from_mp3(file_name + ".mp3")
    
    audio_file_name = os.path.join(TEMP_FOLDER, file_name + ".wav")
    audio.export(audio_file_name, format="wav")
    delete_temp_mp3(file_name)
    
    print("audio_file_name: ", audio_file_name)
    
    print("removing noizies ")
    audio_file_name = await process_audio(audio_file_name)
    
    return audio_file_name


def delete_temp_mp3(filename):
    mp3_filename = f"{filename}.mp3"
    os.remove(mp3_filename)


def download_single_archive(archive, session):

    base_url = "https://www.broadcastify.com"
    try:
        archive_id = archive['id']
        response = session.get(
            f"{base_url}/archives/downloadv2/{archive_id}"
        )  # download the mp3 file
        filename = asyncio.run(save_and_convert_to_wav(
            io.BytesIO(response.content), archive_id
        ))  # save and convert to wav, run the coroutine
        archive['filename'] = filename
        return archive
    except Exception as e:
        print(e)
        return None


async def download_archives_sync(session, archive_list, num_workers=10):
    loop = asyncio.get_event_loop()
    result = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        tasks = [loop.run_in_executor(executor, download_single_archive, archive, session) 
                 for archive in archive_list]
        for result_task in await asyncio.gather(*tasks):
            if result_task:
                result.append(result_task)
    return result


async def parse_date_archive(feedId, date=datetime.datetime.now()):
    username = "alertai"
    password = "Var+(n42421799)"
    action = "auth"
    redirect = "https://www.broadcastify.com/"
    
    s = requests.Session()

    base_url = "https://www.broadcastify.com"
    login_url = "https://m.broadcastify.com/login/"
    payload = {
        "username": username,
        "password": password,
        "action": action,
        "redirect": redirect,
    }
    s.post(
        login_url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    # verify if this is successful
    if s.cookies.get("bcfyuser1", default=None) is None:
        print("Login failed")
        return
    print("Login successful")

    archive_list = await get_full_day_archives(
        s,
        feedId=feedId,
        date=date,
    )
    
    print(archive_list)

    # download full day archive
    
    archive_list = await download_archives_sync(s, archive_list)
    
    return archive_list

async def download(feedId):
    # parse last 10 days of data
    result = []
    for i in range(1, 2):
        print("feedId: ", feedId);
        result.extend(await parse_date_archive(feedId, datetime.datetime.now() - datetime.timedelta(days=i)))
    return result

# Example usage:
# asyncio.run(download(your_feed_id))