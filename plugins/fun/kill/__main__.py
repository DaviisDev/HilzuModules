""" kill animation """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

# by Harsh , inspired by brain.py

import asyncio

from hydrogram import enums

from userge import userge


@userge.cmd("kill$", about={'header': "Kill anybody With Full Power ;-)"})
async def kill_func(message):
    animation_chars = [
        "killing...",
        "Ｆｉｉｉｉｉｒｅ",
        "(　･ิω･ิ)︻デ═一-->",
        "------>_____________",
        "--------->___⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠⁠_______",
        "-------------->_____",
        "------------------->",
        "------>;(^。^)ノ",
        "(￣ー￣) DED",
        "<b>Target killed successfully (´°̥̥̥̥̥̥̥̥ω°̥̥̥̥̥̥̥̥｀)</b>",
    ]
    for i in range(10):
        await asyncio.sleep(0.6)
        await message.edit(animation_chars[i % 10], parse_mode=enums.ParseMode.HTML)
