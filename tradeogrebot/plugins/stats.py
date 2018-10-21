import tradeogrebot.labels as lbl

from coinmarketcap import Market
from telegram import ParseMode
from telegram.ext import RegexHandler
from tradeogrebot.plugin import TradeOgreBotPlugin


class Stats(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_stats_handler()]

    def _get_stats_handler(self):
        return RegexHandler(f"^({lbl.BTN_STATS})$", self._stats)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _stats(self, bot, update):
        user_id = update.message.from_user.id
        data = self.db.get_user_data(user_id)
        coins = data.pair.split("-")

        coin_id = None
        listings = Market().listings()
        for listing in listings["data"]:
            if coins[1].upper() == listing["symbol"].upper():
                coin_id = listing["id"]
                break

        ticker = Market().ticker(coin_id, convert=coins[0])

        coin = ticker["data"]
        symbol = coin["symbol"]
        slug = coin["website_slug"]
        rank = str(coin["rank"])
        sup_c = "{0:,}".format(int(coin["circulating_supply"]))
        sup_t = "{0:,}".format(int(coin["total_supply"]))

        usd = coin["quotes"]["USD"]
        p_usd = "{0:.8f}".format(usd["price"])
        v_24h = "{0:,}".format(int(usd["volume_24h"]))
        m_cap = "{0:,}".format(int(usd["market_cap"]))
        c_1h = str(usd["percent_change_1h"])
        c_24h = str(usd["percent_change_24h"])
        c_7d = str(usd["percent_change_7d"])

        btc = coin["quotes"][coins[0]]
        p_btc = "{0:.8f}".format(float(btc["price"]))

        update.message.reply_text(
            text=f"`{symbol} {p_usd} USD | {p_btc} {coins[0]}\n"
                 f"1h {c_1h}% | 24h {c_24h}% | 7d {c_7d}%\n\n"
                 f"CMC Rank: {rank}\n"
                 f"Volume 24h: {v_24h} USD\n"
                 f"Market Cap: {m_cap} USD\n"
                 f"Circ. Supp: {sup_c} {symbol}\n"
                 f"Total Supp: {sup_t} {symbol}`\n\n"
                 f"[Stats from CoinMarketCap](https://coinmarketcap.com/currencies/{slug})",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
