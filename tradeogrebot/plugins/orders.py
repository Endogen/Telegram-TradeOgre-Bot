import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl

from tradeogrebot.api.tradeogre import TradeOgre
from tradeogrebot.plugin import TradeOgreBotPlugin
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import RegexHandler, CallbackQueryHandler


class Orders(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_orders_handler(), self._get_orders_callback_handler()]

    def _get_orders_handler(self):
        return RegexHandler(f"^({lbl.BTN_ORDERS})$", self._orders)

    def _get_orders_callback_handler(self):
        regex = "^[a-z0-9]{8}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{12}$"
        return CallbackQueryHandler(self._callback_orders, pattern=regex)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.check_keys
    @TradeOgreBotPlugin.send_typing_action
    def _orders(self, bot, update):
        user_id = update.message.from_user.id
        data = self.db.get_user_data(user_id)

        coins = data.pair.split("-")
        orders = TradeOgre().orders(market=data.pair, key=data.api_key, secret=data.api_secret)

        if orders:
            for o in orders:
                update.message.reply_text(
                    text=f"`{o['type']} {o['quantity']} {coins[1]}\n@ {o['price']} {coins[0]}`",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self._keyboard_order_close(o["uuid"]))
        else:
            update.message.reply_text(
                text="No open orders",
                reply_markup=self.keyboard_main())

    @TradeOgreBotPlugin.send_typing_action
    def _callback_orders(self, bot, update):
        query = update.callback_query
        data = self.db.get_user_data(query.message.chat_id)

        close_order = TradeOgre().cancel(
            query.data,
            key=data.api_key,
            secret=data.api_secret)

        if not self.trade_ogre_api_error(close_order, update):
            bot.edit_message_text(
                text=f"`{query.message.text}`\n"
                     f"{emo.CANCEL} *Order closed*",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                parse_mode=ParseMode.MARKDOWN)

    def _keyboard_order_close(self, uuid):
        keyboard_markup = [[InlineKeyboardButton("Close order", callback_data=uuid)]]
        return InlineKeyboardMarkup(keyboard_markup)
