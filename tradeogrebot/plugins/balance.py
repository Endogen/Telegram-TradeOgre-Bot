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
    @TradeOgreBotPlugin.check_keys
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _balance(self, bot, update, data):
        tr = TradeOgre(key=data.api_key, secret=data.api_secret)
        act_coin = data.pair.split("-")[1].upper()

        all_msg = "Other coins\n"
        act_msg = "Active coin\n"

        for coin, value in tr.balances()["balances"].items():
            if coin == act_coin:
                act_msg += f"`{coin}: {self.trm_zro(value)}\n`"
            elif self.trm_zro(value) is not "0":
                all_msg += f"`{coin}: {self.trm_zro(value)}\n`"

        update.message.reply_text(text=all_msg, parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text(text=act_msg, parse_mode=ParseMode.MARKDOWN)
