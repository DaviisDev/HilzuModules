"""MEDIA INFO"""

# Suggested by - @d0n0t (https://github.com/code-rgb/USERGE-X/issues/9)
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import os

from html_telegraph_poster import TelegraphPoster

from userge import Message, userge
from userge.utils import runcmd


@userge.cmd("mediainfo", about={"header": "Get Detailed Info About Replied Media"}, allow_via_bot=False)
async def mediainfo(message: Message):
    """Get Media Info"""
    reply = message.reply_to_message
    if not reply:
        await message.err("reply to media first", del_in=5)
        return
    await message.edit("`Processing ...`")
    x_media = None
    available_media = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
        "new_chat_photo",
    )
    for kind in available_media:
        x_media = getattr(reply, kind, None)
        if x_media is not None:
            break
    if x_media is None:
        await message.err("Reply To a Vaild Media Format", del_in=3)
        return
    media_type = str(type(x_media)).split("'")[1]
    file_path = safe_filename(await reply.download())
    output_ = await runcmd(f'mediainfo "{file_path}"')
    out = None
    if len(output_) != 0:
        out = output_[0]
    body_text = f"""
<h2>JSON</h2>
<pre>{x_media}</pre>
<br>

<h2>DETAILS</h2>
<pre>{out or 'Not Supported'}</pre>
"""
    text_ = media_type.split(".")[-1].upper()
    link = post_to_telegraph(media_type, body_text)
    await message.edit(f"ℹ️  <b>MEDIA INFO:  [{text_}]({link})</b>")
    os.remove(file_path)


def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename


def post_to_telegraph(a_title: str, content: str) -> str:
    """ Create a Telegram Post using HTML Content """
    post_client = TelegraphPoster(use_api=True)
    auth_name = "@HilzuUB"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://telegram.me/HilzuUB",
        text=content
    )
    return post_page['url']
