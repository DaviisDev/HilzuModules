""" Wallpaper Module """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

import requests

from userge import userge, Message, pool


@userge.on_cmd("wall", about={
    'header': "Search Wallpaper",
    'flags': {
        '-l': "Limit of Wallpapers",
        '-doc': "Send as Documents (Recommended)"
    },
    'description': 'Search and Download Hd Wallpaper from AlphaCoders and upload to Telegram',
    'usage': "{tr}wall [Query]",
    'examples': "{tr}wall kanna"})
async def wall_(msg: Message):
    limit = min(int(msg.flags.get('-l', 1)), 10)
    if msg.filtered_input_str:
        qu = msg.filtered_input_str
        await msg.edit(f"__searching wallpapers__ ... `{qu}`")
        for i in range(limit):
            results = requests.get(f"https://kuuhaku-api-production.up.railway.app/api/wallpaper?query={qu}")
            if results.status_code != 200:
                return await msg.edit('**Result Not Found**')
            _json = results.json()['url']
            if '-doc' in msg.flags:
                await msg.send_document(_json)
            else:
                await msg.send_photo(_json)
    else:
        await msg.edit('**Give me Something to search.**')
        await msg.reply_sticker('CAADAQADmQADTusQR6fPCVZ3EhDoFgQ')
