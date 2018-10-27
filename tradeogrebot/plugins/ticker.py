import tradeogrebot.labels as lbl

from telegram import ParseMode
from telegram.ext import RegexHandler
from tradeogrebot.api.tradeogre import TradeOgre
from tradeogrebot.plugin import TradeOgreBotPlugin


class Ticker(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_ticker_handler()]

    def _get_ticker_handler(self):
        return RegexHandler(f"^({lbl.BTN_TICKER})$", self._ticker)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _ticker(self, bot, update, data):
        ticker = TradeOgre().ticker(data.pair)

        if not self.trade_ogre_api_error(ticker, update):
            coins = data.pair.split("-")
            update.message.reply_text(
                text=f"`{coins[1]}: {ticker['price']} {coins[0]}`",
                parse_mode=ParseMode.MARKDOWN)
