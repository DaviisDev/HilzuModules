""" hash , encode and decode """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

import pybase64

from userge import userge, Message
from userge.utils import runcmd


@userge.cmd("hash", about={
    'header': "find hash of text",
    'description': "Find the md5, sha1, sha256, sha512 of the string when written into a txt file",
    'usage': "{tr}hash [text or reply to msg]"})
async def gethash(message: Message):
    """ find hash of text """
    input_ = message.input_or_reply_str
    if not input_:
        await message.err("input not found!")
        return
    with open("hash.txt", "w+") as hashtxt:
        hashtxt.write(input_)
    md5 = (await runcmd("md5sum hash.txt"))[0].split()[0]
    sha1 = (await runcmd("sha1sum hash.txt"))[0].split()[0]
    sha256 = (await runcmd("sha256sum hash.txt"))[0].split()[0]
    sha512 = (await runcmd("sha512sum hash.txt"))[0].split()[0]
    await runcmd("rm hash.txt")
    ans = (f"**Text** : `{input_}`\n**MD5** : `{md5}`\n**SHA1** : `{sha1}`\n"
           f"**SHA256** : `{sha256}`\n**SHA512** : `{sha512}`")
    await message.edit_or_send_as_file(ans, filename="hash.txt", caption="hash.txt")


@userge.cmd("base64", about={
    'header': "Find the base64 encoding of the given string",
    'usage': "{tr}base64 [text or reply to msg] : encode\n"
             "{tr}base64 -d [text or reply to msg] : decode"}, del_pre=True)
async def endecrypt(message: Message):
    """ encode or decode """
    if message.reply_to_message:
        input_ = message.reply_to_message.text
    else:
        input_ = message.filtered_input_str
    if not input_:
        await message.err("input not found!")
        return
    if 'd' in message.flags:
        out = str(pybase64.b64decode(bytes(input_, "utf-8"), validate=True))[2:-1]
        await message.edit(f"**Decoded** : `{out}`")
    else:
        out = str(pybase64.b64encode(bytes(input_, "utf-8")))[2:-1]
        await message.edit(f"**Encoded** : `{out}`")
