""" view or mentions admins """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

from userge import userge, Message
from hydrogram import enums


@userge.cmd("admins", about={
    'header': "View or mention admins in chat",
    'flags': {
        '-m': "mention all admins",
        '-mc': "only mention creator",
        '-id': "show ids"},
    'usage': "{tr}admins [any flag] [chatid]"}, allow_channels=False)
async def mentionadmins(message: Message):
    mentions = "🛡 **Admin List** 🛡\n"
    chat_id = message.filtered_input_str
    flags = message.flags
    men_admins = '-m' in flags
    men_creator = '-mc' in flags
    show_id = '-id' in flags
    if not chat_id:
        chat_id = message.chat.id
    try:
        async for x in message.client.get_chat_members(
                chat_id=chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            status = x.status
            u_id = x.user.id
            username = x.user.username or None
            full_name = (await message.client.get_user_dict(u_id))['flname']
            if status == enums.ChatMemberStatus.OWNER:
                if men_admins or men_creator:
                    mentions += f"\n 👑 [{full_name}](tg://user?id={u_id})"
                elif username:
                    mentions += f"\n 👑 [{full_name}](https://t.me/{username})"
                else:
                    mentions += f"\n 👑 {full_name}"
                if show_id:
                    mentions += f" `{u_id}`"
            elif status == enums.ChatMemberStatus.ADMINISTRATOR:
                if men_admins:
                    mentions += f"\n ⚜ [{full_name}](tg://user?id={u_id})"
                elif username:
                    mentions += f"\n ⚜ [{full_name}](https://t.me/{username})"
                else:
                    mentions += f"\n ⚜ {full_name}"
                if show_id:
                    mentions += f" `{u_id}`"
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await message.delete()
    await message.client.send_message(
        chat_id=message.chat.id, text=mentions, disable_web_page_preview=True)
