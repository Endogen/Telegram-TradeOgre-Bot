import tradeogrebot.labels as lbl

from telegram import ParseMode
from telegram.ext import RegexHandler
from tradeogrebot.api.tradeogre import TradeOgre
from tradeogrebot.plugin import TradeOgreBotPlugin


class Balance(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_balance_handler()]

    def _get_balance_handler(self):
        return RegexHandler(f"^({lbl.BTN_BALANCE})$", self._balance)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.check_keys
    @TradeOgreBotPlugin.send_typing_action
    def _balance(self, bot, update, data):
        coin = data.pair.split("-")[1].upper()
        balance = TradeOgre().balance(coin, key=data.api_key, secret=data.api_secret)

        if not self.trade_ogre_api_error(balance, update):
            update.message.reply_text(
                text=f"`{coin}: {balance['balance']}\n"
                     f"(Avail. {balance['available']})`",
                parse_mode=ParseMode.MARKDOWN)
