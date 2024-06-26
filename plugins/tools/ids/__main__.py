""" get ids """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

from userge import userge, Message


@userge.cmd("ids", about={
    'header': "display ids",
    'usage': "reply {tr}ids any message, file or just send this command"})
async def getids(message: Message):
    msg = message.reply_to_message or message
    out_str = f"👥 **Chat ID** : `{(msg.forward_from_chat or msg.chat).id}`\n"
    out_str += f"💬 **Message ID** : `{msg.forward_from_message_id or msg.id}`\n"
    if msg.from_user:
        out_str += f"🙋‍♂️ **From User ID** : `{msg.from_user.id}`\n"
    if msg.sender_chat:
        out_str += f"👥 **Channel ID** : `{msg.sender_chat.id}`\n"
    file_id = None
    if msg.audio:
        type_ = "audio"
        file_id = msg.audio.file_id
    elif msg.animation:
        type_ = "animation"
        file_id = msg.animation.file_id
    elif msg.document:
        type_ = "document"
        file_id = msg.document.file_id
    elif msg.photo:
        type_ = "photo"
        file_id = msg.photo.file_id
    elif msg.sticker:
        type_ = "sticker"
        file_id = msg.sticker.file_id
    elif msg.voice:
        type_ = "voice"
        file_id = msg.voice.file_id
    elif msg.video_note:
        type_ = "video_note"
        file_id = msg.video_note.file_id
    elif msg.video:
        type_ = "video"
        file_id = msg.video.file_id
    if file_id is not None:
        out_str += f"📄 **Media Type:** `{type_}`\n"
        out_str += f"📄 **File ID:** `{file_id}`"
    await message.edit(out_str)
