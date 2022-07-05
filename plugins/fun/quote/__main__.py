# Rewrote with experimental bleck magik
# code-rgb

from pyrogram.errors import YouBlockedUser

from userge import Message, userge
from userge.utils.exceptions import StopConversation


@userge.on_cmd(
    "q",
    about={
        "header": "Quote message",
        "flags": {"-l": "limit"},
        "usage": "reply {tr}q -l[limit]",
        "examples": ["{tr}q", "{tr}q -l3"],
    },
    allow_via_bot=False,
    del_pre=True,
)
async def quotecmd(message: Message):
    """quotecmd"""
    reply = message.reply_to_message
    quote_list = []
    self_mid = False
    args = ""
    if reply:
        if "l" in message.flags:
            limit = message.flags.get("l", 1)
            if not limit.isdigit():
                await message.err("give valid no. of message to quote", del_in=5)
                return
            num_ = min(int(limit), 24)
            async for msg in userge.iter_history(
                message.chat.id, limit=num_, offset_id=reply.id, reverse=True
            ):
                if msg.id != message.id:
                    quote_list.append(msg.id)
            if message.filtered_input_str:
                self_mid = True
                await message.edit(message.filtered_input_str)
        else:
            quote_list.append(reply.id)
            if message.input_str:
                self_mid = True
                await message.edit(message.input_str)
    else:
        args = message.input_str
    if self_mid:
        quote_list.append(message.id)
    else:
        await message.delete()
    if not args and len(quote_list) == 0:
        await message.err("Reply message or input text !", del_in=5)
        return
    try:
        async with userge.conversation("QuotLyBot", timeout=100) as conv:
            try:
                if quote_list:
                    await userge.forward_messages(
                        "QuotLyBot", message.chat.id, quote_list
                    )
                    if self_mid:
                        await message.delete()
                elif args:
                    await conv.send_message(args)
            except YouBlockedUser:
                await message.edit("first **unblock** @QuotLyBot")
                return
            quote = await conv.get_response(mark_read=True)
            if not (quote.sticker or quote.document):
                await message.err("something went wrong!")
                return
            id = reply.id if reply else None
            if quote.sticker:
                await userge.send_sticker(
                    chat_id=message.chat.id,
                    sticker=quote.sticker.file_id,
                    reply_to_id=id,
                )
            else:
                await userge.send_document(
                    chat_id=message.chat.id,
                    document=quote.document.file_id,
                    reply_to_id=id,
                )
    except StopConversation:
        await message.err(
            "@QuotLyBot Didn't respond in time\n:(  please try again later...", del_in=5
        )