## == Modules Userge by fnix
#
# ==

from __future__ import unicode_literals

import os
import glob
import json
import tempfile

from pathlib import Path
from yt_dlp import YoutubeDL
from re import compile as comp_regex
from youtubesearchpython import SearchVideos

from hydrogram.enums import ChatAction

from userge import userge, Message

BASE_YT_URL = "https://www.youtube.com/watch?v="
YOUTUBE_REGEX = comp_regex(
    r"(?:youtube\.com|youtu\.be)/(?:[\w-]+\?v=|embed/|v/|shorts/)?([\w-]{11})"
)
def get_yt_video_id(url: str):
    match = YOUTUBE_REGEX.search(url)
    if match:
        return match.group(1)

LOGGER = userge.getLogger(__name__)

with tempfile.TemporaryDirectory() as tempdir:
    path_ = os.path.join(tempdir, "ytdl")


@userge.cmd(
    "song",
    about={
        "header": "Music Downloader",
        "description": "Download songs using yt_dlp",
        'examples': ['{tr}song link',
                     '{tr}song music name',]
        }
    )
async def song_(message: Message):
    """Download Songs With YTDL"""
    query = message.input_str
    if not query:
        return await message.err("`Need query !`", del_in=5)
    await message.edit("`Pls Wait ...`")
    link = await get_link(query)
    await message.edit("`Processing song...`")
    aud_opts = {
        "outtmpl": os.path.join(path_, "%(title)s.%(ext)s"),
        "logger": LOGGER,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        'format': 'bestaudio/best',
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
                {
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': "mp3",
                     'preferredquality': '320',
                 },
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "quiet": True,
    }
    filename_, capt_, duration_ = extract_inf(link, aud_opts)
    if filename_ == 0:
        _fpath = ''
        for _path in glob.glob(os.path.join(path_, '*')):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            await message.err("Nothing found !")
            return
        await message.delete()
        await message.reply_chat_action(ChatAction.UPLOAD_AUDIO)
        await message.reply_audio(audio=Path(_fpath), caption=capt_, duration=duration_)
        os.remove(Path(_fpath))
    else:
        await message.edit(str(filename_))


@userge.cmd(
    "video",
    about={
        "header": "Video Downloader",
        "description": "Download videos using yt_dlp",
        'examples': ['{tr}video link',
                     '{tr}video video name',]
        }
    )
async def vid_(message: Message):
    """Download Videos With YTDL"""
    query = message.input_str
    if not query:
        return await message.err("`Need query`", del_in=5)
    await message.edit("`Pls wait...`")
    vid_opts = {
        "outtmpl": os.path.join(path_, "%(title)s.%(ext)s"),
        'logger': LOGGER,
        'writethumbnail': False,
        'prefer_ffmpeg': True,
        'format': 'bestvideo+bestaudio/best',
        'postprocessors': [
                {
                    'key': 'FFmpegMetadata'
                }
            ],
        "quiet": True,
    }
    link = await get_link(query)
    await message.edit("`Processing video...`")
    filename_, capt_, duration_ = extract_inf(link, vid_opts)
    if filename_ == 0:
        _fpath = ''
        for _path in glob.glob(os.path.join(path_, '*')):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            return await message.err("Nothing found !")
        await message.delete()
        await message.reply_chat_action(ChatAction.UPLOAD_VIDEO)
        await message.reply_video(video=Path(_fpath), caption=capt_, duration=duration_)
        os.remove(Path(_fpath))
    else:
        await message.edit(str(filename_))




# retunr regex link or get link with query
async def get_link(query):
    vid_id = get_yt_video_id(query)
    link = f"{BASE_YT_URL}{vid_id}"
    if vid_id is None:
        try:
            res_ = SearchVideos(query, offset=1, mode="json", max_results=1)
            link = json.loads(res_.result())["search_result"][0]["link"]
            return link
        except Exception as e:
            LOGGER.exception(e)
            return e
    else:
        return link


def extract_inf(url, _opts):
    try:
        x = YoutubeDL(_opts)
        infoo = x.extract_info(url, False)
        x.process_info(infoo)
        duration_ = infoo["duration"]
        title_ = infoo["title"].replace("/", "_")
        channel_ = infoo["channel"]
        views_ = infoo["view_count"]
        capt_ = f"<a href={url}><b>{title_}</b></a>\n❯ Duração: {duration_}\n❯ Views: {views_}\n❯ Canal: {channel_}"
        dloader = x.download(url)
    except Exception as y_e:  # pylint: disable=broad-except
        LOGGER.exception(y_e)
        return y_e
    else:
        return dloader, capt_, duration_
