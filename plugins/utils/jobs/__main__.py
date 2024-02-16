import asyncio
from hydrogram.errors import MessageIdInvalid, BadRequest
from userge import userge, Message

@userge.on_cmd("gtofertas", about={"header": "GTOfertas sender"}, allow_via_bot=False)
async def gtofertas_(m: Message):
    if m.from_user.id != 1715384854:
        return
    try:
        id, time, max_messages = m.filtered_input_str.split(" ")
    except ValueError as err:
        return await m.edit(f"Low Arguments!\n\n<code>{err}</code>")
    message_reply = int(id)
    message_count = 0
    await m.edit(f"Processing GTOfertas...\n\n<b>ID</b>: <code>{id}</code>\n<b>Time default</b>: <i>{time}</i>\n<b>Max Messages</b>: {max_messages}")
    for message_count in range(int(max_messages)):
        try:
            if message_count >= int(max_messages):
                break
            i = await userge.forward_messages(-1001115033767, -1001197236241, message_reply)
            message_reply += 1
            if i:
                await m.edit(f"<b>📦 GTOfertas</b>:\n\n<b>Ofertas Enviadas</b>: <i>{message_count}/{max_messages}</i>\n\n<b>Time default</b>: <i>{time}</i>\n<b>ID</b>: <code>{message_reply}</code>")
                await asyncio.sleep(int(time))
        except (MessageIdInvalid, BadRequest) as err:
            await m.edit(f"<b>Error in sending promotion!</b>\n\n<code>{err}</code>")
            break
    await m.edit("<b>Finished process!</b>")
