## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

import os
import re
import json
import asyncio
import logging
import requests
import shutil
import wget
import tempfile

from yt_dlp import YoutubeDL
from yt_dlp.utils import GeoRestrictedError, ExtractorError, DownloadError
from uuid import uuid4
from typing import Callable, List, Any, Dict, Union
from collections import defaultdict
from functools import wraps, partial
from youtubesearchpython.__future__ import VideosSearch

from hydrogram import filters
from hydrogram.errors import MessageIdInvalid, MessageNotModified
from hydrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    InputMediaPhoto,
    InputMediaAudio,
    InputMediaVideo,
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent
)

from userge import Message, config as Config, userge
from ...builtin import sudo


YT = "https://www.youtube.com/"
YT_VID_URL = YT + "watch?v="


def aiowrap(func: Callable) -> Callable:
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

def sublists(input_list: List[Any], width: int = 3) -> List[List[Any]]:
    """retuns a single list of multiple sublist of fixed width"""
    return [input_list[x : x + width] for x in range(0, len(input_list), width)]
          

@aiowrap
def extract_info(instance: YoutubeDL, url: str, download=True):
    return instance.extract_info(url, download)

def humanbytes(size: float) -> str:
    """humanize size"""
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])

class Buttons(InlineKeyboardMarkup):
    def __init__(self, inline_keyboard: List[List["InlineKeyboardButton"]]):
        super().__init__(inline_keyboard)

    def __add__(self, extra: Union[str, int]) -> InlineKeyboardMarkup:
        """Add extra Data to callback_data of every button

        Parameters:
        ----------
            - extra (`Union[str, int]`): Extra data e.g A `key` or `user_id`.

        Raises:
        ------
            `TypeError`

        Returns:
        -------
            `InlineKeyboardMarkup`: Modified markup
        """
        if not isinstance(extra, (str, int)):
            raise TypeError(
                f"unsupported operand `extra` for + : '{type(extra)}' and '{type(self)}'"
            )
        ikb = self.inline_keyboard
        cb_extra = f"-{extra}"
        for row in ikb:
            for btn in row:
                if (
                    (cb_data := btn.callback_data)
                    and cb_data.startswith("yt_")
                    and not cb_data.endswith(cb_extra)
                ):
                    cb_data += cb_extra
                    btn.callback_data = cb_data[:64]  # limit: 1-64 bytes.
        return InlineKeyboardMarkup(ikb)

    def add(self, extra: Union[str, int]) -> InlineKeyboardMarkup:
        """Add extra Data to callback_data of every button

        Parameters:
        ----------
            - extra (`Union[str, int]`): Extra data e.g A `key` or `user_id`.

        Raises:
        ------
            `TypeError`

        Returns:
        -------
            `InlineKeyboardMarkup`: Modified markup
        """
        return self.__add__(extra)

class SearchResult:
    def __init__(
        self,
        key: str,
        text: str,
        image: str,
        buttons: InlineKeyboardMarkup,
    ) -> None:
        self.key = key
        self.buttons = Buttons(buttons.inline_keyboard)
        self.caption = text
        self.image_url = image

    def __repr__(self) -> str:
        out = self.__dict__.copy()
        out["buttons"] = (
            json.loads(str(btn)) if (btn := out.pop("buttons", None)) else None
        )
        return json.dumps(out, indent=4)

class YT_DLP:
    async def get_download_button(self, yt_id: str, user_id: int) -> SearchResult:
        buttons = [
            [
                InlineKeyboardButton(
                    "🥇 BEST - 🎥 MP4",
                    callback_data=f"yt_dl|{yt_id}|mp4|{user_id}|v",
                ),
            ]
        ]
        best_audio_btn = [
            [
                InlineKeyboardButton(
                    "🥇 BEST - 📀 320Kbps - MP3",
                    callback_data=f"yt_dl|{yt_id}|mp3|{user_id}|a",
                )
            ]
        ]

        params = {"no-playlist": True, "quiet": True, "logtostderr": False}

        try:
            # //
            vid_data = await extract_info(
                YoutubeDL(params), f"{YT_VID_URL}{yt_id}", download=False
            )
        except ExtractorError:
            vid_data = None
            buttons += best_audio_btn
        else:
            # ------------------------------------------------ #
            qual_dict = defaultdict(lambda: defaultdict(int))
            qual_list = ("1440p", "1080p", "720p", "480p", "360p", "240p", "144p")
            audio_dict: Dict[int, str] = {}
            # ------------------------------------------------ #
            for video in vid_data["formats"]:
                fr_note = video.get("format_note")
                fr_id = video.get("format_id")
                fr_size = video.get("filesize")
                if video.get("ext") == "mp4":
                    for frmt_ in qual_list:
                        if fr_note in (frmt_, frmt_ + "140"):
                            qual_dict[frmt_][fr_id] = fr_size
                if video.get("acodec") != "none":
                    bitrrate = video.get("abr")
                    if bitrrate == (0 or "None"):
                        pass
                    else:
                        audio_dict[
                            bitrrate
                        ] = f"📀 {bitrrate}Kbps ({humanbytes(fr_size) or 'N/A'})"
            audio_dict = await self.delete_none(audio_dict)
            video_btns: List[InlineKeyboardButton] = []
            for frmt in qual_list:
                frmt_dict = qual_dict[frmt]
                if len(frmt_dict) != 0:
                    frmt_id = sorted(list(frmt_dict))[-1]
                    frmt_size = humanbytes(frmt_dict.get(frmt_id)) or "N/A"
                    video_btns.append(
                        InlineKeyboardButton(
                            f"🎥 {frmt} ({frmt_size})",
                            callback_data=f"yt_dl|{yt_id}|{frmt_id}+140|{user_id}|v",
                        )
                    )
            buttons += sublists(video_btns, width=2)
            buttons += best_audio_btn
            buttons += sublists(
                list(
                    map(
                        lambda x: InlineKeyboardButton(
                            audio_dict[x], callback_data=f"yt_dl|{yt_id}|{x}|{user_id}|a"
                        ),
                        sorted(audio_dict.keys(), reverse=True),
                    )
                ),
                width=2,
            )

        return SearchResult(
            yt_id,
            (
                f"<a href={YT_VID_URL}{yt_id}>{vid_data.get('title')}</a>"
                if vid_data
                else ""
            ),
            vid_data.get("thumbnail")
            if vid_data
            else "https://s.clipartkey.com/mpngs/s/108-1089451_non-copyright-youtube-logo-copyright-free-youtube-logo.png",
            InlineKeyboardMarkup(buttons),
        )

    @aiowrap
    def delete_none(self, _dict):
        """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
        if isinstance(_dict, dict):
            for key, value in list(_dict.items()):
                if isinstance(value, (list, dict, tuple, set)):
                    _dict[key] = self.delete_none(value)
                elif value is None or key is None:
                    del _dict[key]

        elif isinstance(_dict, (list, set, tuple)):
            _dict = type(_dict)(self.delete_none(item) for item in _dict if item is not None)

        return _dict
    
    async def downloader(self, url: str, options: [str, Any]): # type: ignore
        try:
            down =  await extract_info(YoutubeDL(options), url, download=True)
            file = down.get("requested_downloads")[0]["filepath"] 
            duration = down.get("duration")
            title = down.get("fulltitle")
            return file, duration, title
        except DownloadError:
            logging.error("[DownloadError] : Failed to Download Media")
        except GeoRestrictedError:
            logging.error(
                "[GeoRestrictedError] : The uploader has not made this video"
                " available in your country"
            )
        except Exception as e:
            logging.exception("YouTuber: Something Went Wrong: {}".format(e))

    @aiowrap
    def rand_key(self):
        return str(uuid4())[:8]
    
    @aiowrap
    def get_ytthumb(self, videoid: str):
        thumb_quality = [
            "maxresdefault.jpg",  # Best quality
            "hqdefault.jpg",
            "sddefault.jpg",
            "mqdefault.jpg",
            "default.jpg",  # Worst quality
        ]
        thumb_link = "https://i.imgur.com/4LwPLai.png"
        for qualiy in thumb_quality:
            link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
            if requests.get(link).status_code == 200:
                thumb_link = link
                break
        return thumb_link


if userge.has_bot:
    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and c_q.from_user.id in (list(Config.OWNER_ID) + list(sudo.USERS)):
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)
                except MessageIdInvalid:
                    await c_q.answer("Sorry, I Don't Have Permissions to edit this 😔",
                                     show_alert=True)
            else:
                user_dict = await userge.bot.get_user_dict(Config.OWNER_ID[0])
                await c_q.answer(
                    f"Only {user_dict['flname']} Can Access this...! Build Your Own @fnixsup 🤘",
                    show_alert=True)
        return wrapper

    # https://gist.github.com/silentsokolov/f5981f314bc006c82a41
    regex = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
    YT_DB = {}

    @userge.on_cmd(
        "iytdl",
        about={
            'header': "Advanced YTDL",
            'usage': "{tr}iytdl URL or Query"}
    )
    async def iytdl_ub_cmd(m: Message):
        reply = m.reply_to_message
        user_id = m.from_user.id
        query = None
        if m.input_str:
            query = m.input_str
        elif reply:
            if reply.text:
                query = reply.text
            elif reply.caption:
                query = reply.caption
        if not query:
            return await m.err("Input or reply to a valid youtube URL", del_in=5)
        if m.client.is_bot:
            match = regex.match(query)
            if match is None:
                search_key = await YT_DLP().rand_key()
                YT_DB[search_key] = query
                search = await VideosSearch(query).next()
                if search["result"] == []:
                    return await m.err(f"No result found for `{query}`")
                i = search['result'][0]
                out = f"<b><a href={i['link']}>{i['title']}</a></b>"
                out += f"\nPublished {i['publishedTime']}\n"
                out += f"\n<b>❯ Duration:</b> {i['duration']}"
                out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
                out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
                btn = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"1/{len(search['result'])}", callback_data=f"ytdl_scroll|{search_key}|1|{user_id}|")
                        ],
                        [
                            InlineKeyboardButton(
                                "Download", callback_data=f"yt_gen|{i['id']}|{user_id}|")
                        ]
                    ]
                )
                img = await YT_DLP().get_ytthumb(i['id'])
                caption = out
                markup = btn
                await userge.bot.send_photo(m.chat.id, img, caption=caption, reply_markup=markup)
            else:
                key = match.group("id")
                x = await YT_DLP().get_download_button(key, user_id)
                img = await YT_DLP().get_ytthumb(key)
                caption = x.caption
                markup = x.buttons
                await userge.bot.send_photo(m.chat.id, img, caption=caption, reply_markup=markup)
        else:
            await m.delete()
            username = (await userge.bot.get_me()).username
            x = await userge.get_inline_bot_results(username, f"ytdl {query}")
            await userge.send_inline_bot_result(chat_id=m.chat.id, query_id=x.query_id, result_id=x.results[0].id)

    @userge.bot.on_callback_query(filters=filters.regex(pattern=r"ytdl_scroll\|(.*)"))
    @check_owner
    async def ytdl_scroll_callback(cq: CallbackQuery):
        callback = cq.data.split("|")
        search_key = callback[1]
        page = int(callback[2])
        user_id = int(callback[3])
        query = YT_DB[search_key]
        search = await VideosSearch(query).next()
        i = search['result'][page]
        out = f"<b><a href={i['link']}>{i['title']}</a></b>"
        out += f"\nPublished {i['publishedTime']}\n"
        out += f"\n<b>❯ Duration:</b> {i['duration']}"
        out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
        out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
        scroll_btn = [
            [
                InlineKeyboardButton(
                    f"Back", callback_data=f"ytdl_scroll|{search_key}|{page-1}|{user_id}|"),
                InlineKeyboardButton(
                    f"{page+1}/{len(search['result'])}", callback_data=f"ytdl_scroll|{search_key}|{page+1}|{user_id}|")
            ]
        ]
        if page == 0:
            if len(search['result']) == 1:
                return await cq.answer("That's the end of list", show_alert=True)
            scroll_btn = [[scroll_btn.pop().pop()]]
        elif page == (len(search['result'])-1):
            scroll_btn = [[scroll_btn.pop().pop(0)]]
        btn = [
            [
                InlineKeyboardButton(
                    "Download", callback_data=f"yt_gen|{i['id']}|{user_id}|")
            ]
        ]
        btn = InlineKeyboardMarkup(scroll_btn+btn)
        await cq.edit_message_media(InputMediaPhoto(await YT_DLP().get_ytthumb(i['id']), caption=out), reply_markup=btn)

    @userge.bot.on_callback_query(filters=filters.regex(pattern=r"yt_(gen|dl)\|(.*)"))
    @check_owner
    async def ytdl_gendl_callback(cb: CallbackQuery):
        inf = cb.data.split("|")
        key = inf[1]
        try:
            if key[0] == "yt_gen":
                user_id = inf[2] or None
                x = (await YT_DLP().get_download_button(key, user_id))
                await cb.edit_message_caption(caption=x.caption, reply_markup=x.buttons)
            else:
                uid = inf[2]
                type_ = inf[4]
                with tempfile.TemporaryDirectory() as tempdir:
                    path_ = os.path.join(tempdir, "ytdl")
                thumb = wget.download(await YT_DLP().get_ytthumb(key), "userge/xcache" + "thumbnail.png")
                if type_ == "a":
                    format_ = "audio"
                else:
                    format_ = "video"

                await cb.edit_message_caption(caption="<code>Downloading pls...</b>")

                if format_ == "video":
                    options = {
                        "addmetadata": True,
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "outtmpl": os.path.join(path_, "%(title)s-%(format)s.%(ext)s"),
                        "logger": logging,
                        "format": uid,
                        "writethumbnail": True,
                        "prefer_ffmpeg": True,
                        "postprocessors": [{"key": "FFmpegMetadata"}],
                        "quiet": True,
                        "logtostderr": True,
                    }
                    file, duration, title = (await YT_DLP().downloader(
                        url=f"https://www.youtube.com/watch?v={key}", options=options
                    ))

                    
                    await cb.edit_message_media(
                        media=InputMediaVideo(
                            media=file, duration=duration, caption=title, thumb=thumb
                        )
                    )

                elif format_ == "audio":
                    options = {
                        "outtmpl": os.path.join(path_, "%(title)s-%(format)s.%(ext)s"),
                        "logger": logging,
                        "writethumbnail": True,
                        "prefer_ffmpeg": True,
                        "format": "bestaudio/best",
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": uid,
                            },
                            {"key": "EmbedThumbnail"},
                            {"key": "FFmpegMetadata"},
                        ],
                        "quiet": True,
                        "logtostderr": True,
                    }
                    file, duration, title = (await YT_DLP().downloader(
                        url=f"https://www.youtube.com/watch?v={key}", options=options
                    ))

                    await cb.edit_message_caption(
                        caption="<code>Uploading, Please Wait...</code>"
                    )
                    await cb.edit_message_media(
                        media=InputMediaAudio(
                            media=file, duration=duration, caption=title, thumb=thumb
                        )
                    )
                else:
                    await cb.answer("[Format Error] Fail in generate video in this format.", show_alert=True)
                os.remove(thumb)
                shutil.rmtree(tempdir)
        except MessageNotModified:
            return
        except Exception as e:
            logging.error(e)
            return

    @userge.bot.on_inline_query(
        filters.create(
            lambda _, __, inline_query: (
                inline_query.query
                and inline_query.query.startswith("ytdl ")
                and inline_query.from_user.id in (list(Config.OWNER_ID) + list(sudo.USERS))
            ),
            name="iYTDL"
        ),
        group=-2
    )
    async def iytdl_inline(_, iq: InlineQuery):
        query = iq.query.split("ytdl ", 1)[1]
        match = regex.match(query)
        results = []
        user_id = iq.from_user.id
        found_ = True
        if match is None:
            search_key = await YT_DLP().rand_key()
            YT_DB[search_key] = query
            search = (await VideosSearch(query=query).next())
            if len(search["result"]) == 0:
                found_ = False
            else:
                i = search["result"][0]
                key = i['id']
                thumb_ = await YT_DLP().get_ytthumb(key)
                out = f"<b><a href={i['link']}>{i['title']}</a></b>"
                out += f"\nPublished {i['publishedTime']}\n"
                out += f"\n<b>❯ Duration:</b> {i['duration']}"
                out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
                out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
                scroll_btn = [
                    [
                        InlineKeyboardButton(
                            f"1/{len(i)}", callback_data=f"ytdl_scroll|{search_key}|1|{user_id}|")
                    ]
                ]
                if len(i) == 1:
                    scroll_btn = []
                btn = [
                    [
                        InlineKeyboardButton(
                            "Download", callback_data=f"yt_gen|{key}|{user_id}|")
                    ]
                ]
                btn = InlineKeyboardMarkup(scroll_btn+btn)
            if found_:
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=thumb_,
                        thumb_url=thumb_,
                        caption=out,
                        reply_markup=btn,
                    )
                )
            else:
                results.append(
                    InlineQueryResultArticle(
                        title="not found",
                        input_message_content=InputTextMessageContent(
                            f"No result found for `{query}`"
                        ),
                        description="INVALID",
                    )
                )
        else:
            key = match.group("id")
            x = await YT_DLP().get_download_button(key, user_id)
            thumb_ = await YT_DLP().get_ytthumb(key)
            results = [
                InlineQueryResultPhoto(
                    photo_url=thumb_,
                    thumb_url=thumb_,
                    caption=x.caption,
                    reply_markup=x.buttons,
                )
            ]
        await iq.answer(results=results, is_gallery=False, is_personal=True)
        iq.stop_propagation()