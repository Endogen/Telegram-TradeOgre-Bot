import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl

from enum import auto
from tradeogrebot.api.tradeogre import TradeOgre
from tradeogrebot.plugin import TradeOgreBotPlugin
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, ConversationHandler, RegexHandler
from telegram.ext.filters import Filters


class History(TradeOgreBotPlugin):

    SIMULTANEOUS_TRADES = 5
    history = None

    # Conversation handler states
    TRADES_NEXT = auto()

    def get_handlers(self):
        return [self._get_conversation_handler()]

    # TODO: Rename methods to something that makes more sense
    def _get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[RegexHandler(f"^({lbl.BTN_TRADES})$", self._trades)],
            states={
                self.TRADES_NEXT:
                    [RegexHandler(f"^({lbl.BTN_NEXT})$", self._trades_next),
                     RegexHandler(f"^({lbl.BTN_BACK})$", self.back)]
            },
            fallbacks=[MessageHandler(Filters.text, self.back)],
            allow_reentry=True)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _trades(self, bot, update):
        user_id = update.message.from_user.id
        data = self.db.get_user_data(user_id)

        self.history = TradeOgre().history(data.pair)
        self.history = sorted(self.history, key=lambda k: k['date'], reverse=True)

        for trade in range(self.SIMULTANEOUS_TRADES):
            trade = next(iter(self.history), None)

            update.message.reply_text(
                text=self._get_trade_str(trade),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self._keyboard_trades())

            self.history.remove(trade)

        return self.TRADES_NEXT

    def _get_trade_str(self, trade):
        if trade["type"] == "sell":
            return f"{emo.SELL} `{trade['quantity']} @ {trade['price']}`"
        if trade["type"] == "buy":
            return f"{emo.BUY} `{trade['quantity']} @ {trade['price']}`"

    @TradeOgreBotPlugin.send_typing_action
    def _trades_next(self, bot, update):
        for trade in range(self.SIMULTANEOUS_TRADES):
            trade = next(iter(self.history), None)

            update.message.reply_text(
                text=self._get_trade_str(trade),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self._keyboard_trades())

            self.history.remove(trade)

        return self.TRADES_NEXT

    def _keyboard_trades(self):
        buttons = [
            KeyboardButton(lbl.BTN_NEXT),
            KeyboardButton(lbl.BTN_BACK)
        ]

        return ReplyKeyboardMarkup(
            self.build_menu(buttons, n_cols=2),
            resize_keyboard=True)
