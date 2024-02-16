import asyncio
from hydrogram.errors import MessageIdInvalid, BadRequest
from userge import userge, Message

@userge.on_cmd("gtofertas", about={"header": "GTOfertas sender"}, allow_via_bot=False)
async def gtofertas_(m: Message):
    if m.from_user.id != 1715384854:
        return
    try:
        id, time, max_messages = m.filtered_input_str.split("|", maxsplit=1)
    except ValueError as err:
        return await m.edit(f"Low Arguments!\n\n<code>{err}</code>")
    message_reply = int(id)
    message_count = 0
    await m.edit(id, time, max_messages)
    async for message_count in range(max_messages):
        try:
            if message_count >= max_messages:
                break
            i = await userge.forward_messages(to_chat=-1001115033767, from_chat=-1001197236241, messages_ids=message_reply)
            message_reply += 1
            if i:
                 await m.edit(f"<b>📦 GTOfertas</b>:\n\n<b>Ofertas Enviadas</b>: <i>{message_count}/{max_messages}</i>\n\n<b>Time default</b>: <i>{time}</i>\n<b>ID</b>: <code>{message_reply}</code>")
                 await asyncio.sleep(int(time))
        except (MessageIdInvalid, BadRequest) as err:
            await m.edit(f"<b>Error in to send-promotion!</b>\n\n<code>{err}</code>")
            break
        await m.edit("<b>Finished process!</b>")