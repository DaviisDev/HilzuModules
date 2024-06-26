""" English DIctionary telegram """

## == Modules Userge by fnix
#
# = All copyrights to UsergeTeam
#
# ==

import aiohttp

from userge import userge, Message

LOG = userge.getLogger(__name__)  # logger object
CHANNEL = userge.getCLogger(__name__)  # channel logger object


@userge.cmd("dic", about={
    'header': "English Dictionary-telegram",
    'usage': "{tr}dic [word]",
    'examples': 'word : Search for any word'})
async def dictionary(message: Message):
    """this is a dictionary"""
    LOG.info("starting dic command...")
    input_ = message.input_str

    await message.edit("`processing...⚙️🛠`")

    def combine(s_word, name):
        w_word = f"🛑--**__{name.title()}__**--\n"
        for i in s_word:
            if "definition" in i:
                if "example" in i:
                    w_word += ("\n👩‍🏫 **Definition** 👨‍🏫\n<pre>" + i["definition"] +
                               "</pre>\n\t\t❓<b>Example</b>❔\n<pre>" + i["example"] + "</pre>")
                else:
                    w_word += "\n👩‍🏫 **Definition** 👨‍🏫\n" + "<pre>" + i["definition"] + "</pre>"
        w_word += "\n\n"
        return w_word

    def out_print(word1):
        out = ""
        if "meaning" in list(word1):
            meaning = word1["meaning"]
            if "noun" in list(meaning):
                noun = meaning["noun"]
                out += combine(noun, "noun")
            if "verb" in list(meaning):
                verb = meaning["verb"]
                out += combine(verb, "verb")
            if "preposition" in list(meaning):
                preposition = meaning["preposition"]
                out += combine(preposition, "preposition")
            if "adverb" in list(meaning):
                adverb = meaning["adverb"]
                out += combine(adverb, "adverb")
            if "adjective" in list(meaning):
                adjec = meaning["adjective"]
                out += combine(adjec, "adjective")
            if "abbreviation" in list(meaning):
                abbr = meaning["abbreviation"]
                out += combine(abbr, "abbreviation")
            if "exclamation" in list(meaning):
                exclamation = meaning["exclamation"]
                out += combine(exclamation, "exclamation")
            if "transitive verb" in list(meaning):
                transitive_verb = meaning["transitive verb"]
                out += combine(transitive_verb, "transitive verb")
            if "determiner" in list(meaning):
                determiner = meaning["determiner"]
                out += combine(determiner, "determiner")
            if "crossReference" in list(meaning):
                crosref = meaning["crossReference"]
                out += combine(crosref, "crossReference")
        if "title" in list(word1):
            out += ("🔖--**__Error Note__**--\n\n▪️`" + word1["title"] +
                    "🥺\n\n▪️" + word1["message"] + "😬\n\n▪️<i>" + word1["resolution"] +
                    "</i>🤓`")
        return out

    if not input_:
        await message.err("❌Please enter word to search‼️")
    else:
        word = input_
        url = f"https://api.dictionaryapi.dev/api/v1/entries/en/{word}"
        async with aiohttp.ClientSession() as ses, ses.get(url) as res:
            r_dec = await res.json()
        v_word = input_
        if isinstance(r_dec, list):
            r_dec = r_dec[0]
            v_word = r_dec['word']
        last_output = out_print(r_dec)
        if last_output:
            await message.edit("`📌Search result for   `" + f"👉 {v_word}\n\n" + last_output)
            await CHANNEL.log(f"Got dictionary results for 👉 {v_word}")
        else:
            await message.edit('`No result found in the database.😔`', del_in=5)
            await CHANNEL.log("Got dictionary result empty")
