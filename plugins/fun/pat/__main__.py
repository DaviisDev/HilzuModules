""" give head pat """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

from random import choice
from urllib import parse

import aiohttp

from userge import userge, Message


@userge.cmd("pat", about={
    'header': "Give head Pat xD",
    'flags': {'-g': "For Pat Gifs"},
    'usage': "{tr}pat [reply | username]\n{tr}pat -g [reply]"})
async def pat(message: Message):
    username = message.filtered_input_str
    reply = message.reply_to_message
    reply_id = reply.id if reply else message.id
    if not username and not reply:
        await message.edit("**Bruh** ~`Reply to a message or provide username`", del_in=3)
        return
    kwargs = {"reply_to_message_id": reply_id, "caption": username}

    if "-g" in message.flags:
        async with aiohttp.ClientSession() as session, session.get(
            "https://nekos.life/api/pat"
        ) as request:
            result = await request.json()
            link = result.get("url")
            await message.client.send_animation(
                message.chat.id, animation=link, **kwargs
            )
    else:
        async with aiohttp.ClientSession() as session:
            chi_c = await session.get("https://headp.at/js/pats.json")
            uri = f"https://headp.at/pats/{parse.quote(choice(await chi_c.json()))}"
        await message.reply_photo(uri, **kwargs)

    await message.delete()  # hmm
