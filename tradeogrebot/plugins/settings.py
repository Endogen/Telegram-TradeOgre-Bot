import tradeogrebot.labels as lbl

from enum import auto
from coinmarketcap import Market
from tradeogrebot.api.tradeogre import TradeOgre
from tradeogrebot.api.coingecko import CoinGecko
from tradeogrebot.plugin import TradeOgreBotPlugin
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, RegexHandler
from telegram.ext.filters import Filters


class Settings(TradeOgreBotPlugin):

    # Conversation handler states
    SETTINGS_CHOOSE = auto()
    SETTINGS_PAIR = auto()
    SETTINGS_KEY = auto()
    SETTINGS_SECRET = auto()

    def get_handlers(self):
        return [self._get_settings_handler()]

    def _get_settings_handler(self):
        return ConversationHandler(
            entry_points=[RegexHandler(f"^({lbl.SETTINGS})$", self._settings)],
            states={
                self.SETTINGS_CHOOSE:
                    [RegexHandler(f"^({lbl.PAIR})$", self._settings_pair),
                     RegexHandler(f"^({lbl.API_KEYS})$", self._settings_keys),
                     RegexHandler(f"^({lbl.BACK})$", self.back)],
                self.SETTINGS_PAIR:
                    [RegexHandler(f"^({lbl.BACK})$", self.back),
                     MessageHandler(Filters.text, self._settings_pair_save)],
                self.SETTINGS_KEY:
                    [RegexHandler(f"^({lbl.BACK})$", self.back),
                     MessageHandler(Filters.text, self._settings_key_save, pass_user_data=True)],
                self.SETTINGS_SECRET:
                    [RegexHandler(f"^({lbl.BACK})$", self.back),
                     MessageHandler(Filters.text, self._settings_secret_save, pass_user_data=True)]
            },
            fallbacks=[MessageHandler(Filters.text, self.back)],
            allow_reentry=True)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.send_typing_action
    def _settings(self, bot, update):
        user_id = update.message.from_user.id
        data = self.db.get_user_data(user_id)
        pair = data.pair

        if data.api_key and data.api_secret:
            keys = data.api_key[:4] + "... " + data.api_secret[:4] + "... "
        else:
            keys = str(None) + " & " + str(None)

        update.message.reply_text(
            text="*Pair* = Set trading pair\n"
                 "*API Keys* = Set TradeOgre API Keys\n\n"
                 f"Current Status:\n`Pair = {pair}\nKeys = {keys}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self._keyboard_settings())

        return self.SETTINGS_CHOOSE

    @TradeOgreBotPlugin.send_typing_action
    def _settings_pair(self, bot, update):
        pairs = list()

        markets = TradeOgre().markets()

        for pair in markets:
            pairs.append(next(iter(pair.keys())))

        update.message.reply_text(
            text="Choose trading pair",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self._keyboard_pairs(pairs))

        return self.SETTINGS_PAIR

    @TradeOgreBotPlugin.send_typing_action
    def _settings_pair_save(self, bot, update):
        user_id = update.message.from_user.id
        pair = update.message.text.upper()
        self.db.set_pair(user_id, pair)

        update.message.reply_text(
            text="Trading pair saved",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_main())

        self._save_gc_coin_id(user_id, pair)
        self._save_cmc_coin_id(user_id, pair)

        return ConversationHandler.END

    @TradeOgreBotPlugin.send_typing_action
    def _settings_keys(self, bot, update):
        update.message.reply_text(
            text="Enter TradeOgre *API KEY*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_back())

        return self.SETTINGS_KEY

    @TradeOgreBotPlugin.send_typing_action
    def _settings_key_save(self, bot, update, user_data):
        user_data.clear()

        api_key = update.message.text
        user_data["api_key"] = api_key

        update.message.reply_text(
            text="Enter TradeOgre *API SECRET*",
            parse_mode=ParseMode.MARKDOWN)

        return self.SETTINGS_SECRET

    @TradeOgreBotPlugin.send_typing_action
    def _settings_secret_save(self, bot, update, user_data):
        user_id = update.message.from_user.id
        api_key = user_data["api_key"]
        api_secret = update.message.text
        self.db.set_keys(user_id, api_key, api_secret)

        update.message.reply_text(
            text="API keys saved",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_main())

        return ConversationHandler.END

    def _keyboard_settings(self):
        buttons = [
            KeyboardButton(lbl.PAIR),
            KeyboardButton(lbl.API_KEYS),
            KeyboardButton(lbl.BACK)
        ]

        return ReplyKeyboardMarkup(self.build_menu(buttons, n_cols=2), resize_keyboard=True)

    def _keyboard_pairs(self, pairs):
        if pairs:
            return ReplyKeyboardMarkup(
                self.build_menu(pairs, n_cols=3, footer_buttons=[KeyboardButton(lbl.BACK)]),
                resize_keyboard=True)
        else:
            return None

    def _save_gc_coin_id(self, user_id, pair):
        symbol = pair.split("-")[1]
        for coin in CoinGecko().get_coins_list():
            if coin["symbol"].lower() == symbol.lower():
                self.db.set_cg_coin_id(user_id, coin["id"])
                break

    def _save_cmc_coin_id(self, user_id, pair):
        symbol = pair.split("-")[1]
        for listing in Market().listings()["data"]:
            if symbol.upper() == listing["symbol"].upper():
                self.db.set_cmc_coin_id(user_id, listing["id"])
                break
