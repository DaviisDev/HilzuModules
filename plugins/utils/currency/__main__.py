""" convert currency """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

import json

import aiohttp
from emoji import get_emoji_regexp

from hydrogram import enums

from userge import userge, Message
from .. import currency

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


@userge.cmd("cr", about={
    'header': "use this to convert currency & get exchange rate",
    'description': "Convert currency & get exchange rates.",
    'examples': "{tr}cr 1 BTC USD"})
async def cur_conv(message: Message):
    """
    this function can get exchange rate results
    """
    if currency.CURRENCY_API is None:
        await message.edit(
            "<code>Oops!!get the API from</code> "
            "<a href='https://free.currencyconverterapi.com'>HERE</a> "
            "<code>& add it to Heroku config vars</code> (<code>CURRENCY_API</code>)",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML, del_in=0)
        return

    filterinput = get_emoji_regexp().sub(u'', message.input_str)
    curcon = filterinput.upper().split()

    if len(curcon) == 3:
        amount, currency_to, currency_from = curcon
    else:
        await message.err("you entered invalid data")
        return

    if amount.isdigit():
        url = ("https://free.currconv.com/api/v7/convert?"
               f"apiKey={currency.CURRENCY_API}&q="
               f"{currency_from}_{currency_to}&compact=ultra")
        async with aiohttp.ClientSession() as ses, ses.get(url) as res:
            data = json.loads(await res.text())
        try:
            result = data[f'{currency_from}_{currency_to}']
        except KeyError:
            LOG.info(data)
            await message.edit("`invalid response from api !`", del_in=5)
            return
        result = float(amount) / float(result)
        result = round(result, 5)
        await message.edit(
            "**CURRENCY EXCHANGE RATE RESULT:**\n\n"
            f"`{amount}` **{currency_to}** = `{result}` **{currency_from}**")
        await CHANNEL.log("`cr` command executed sucessfully")

    else:
        await message.edit(
            r"`This seems to be some alien currency, which I can't convert right now.. (⊙_⊙;)`",
            del_in=0)
