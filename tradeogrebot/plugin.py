import inspect
import tradeogrebot.labels as lbl
import tradeogrebot.emoji as emo

from typing import List
from enum import IntEnum, auto
from telegram.ext import Handler, ConversationHandler
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton, ChatAction


class TradeOgreBotPlugin:

    def __init__(self, updater, db):
        self.updater = updater
        self.db = db

    # Decorator to show user that bot is retrieving data
    @classmethod
    def send_typing_action(cls, func):
        def _send_typing_action(*args, **kwargs):
            self, bot, update = args

            if update.message:
                user_id = update.message.chat_id
            else:
                user_id = update.callback_query.message.chat_id

            bot.send_chat_action(
                chat_id=user_id,
                action=ChatAction.TYPING)

            return func(self, bot, update, **kwargs)

        return _send_typing_action

    # Decorator to add users if not already present
    @classmethod
    def add_user(cls, func):
        def _add_user(self, bot, update, **kwargs):
            usr = update.message.from_user
            if not self.db.user_exists(usr.id):
                self.db.add_user(usr)

            return func(self, bot, update, **kwargs)
        return _add_user

    # Decorator to check if trading pair is set
    @classmethod
    def check_pair(cls, func):
        def _check_pair(self, bot, update, **kwargs):
            if "data" not in kwargs or not kwargs["data"]:
                user_id = update.effective_user.id
                kwargs["data"] = self.db.get_user_data(user_id)

            if not kwargs["data"].pair:
                update.message.reply_text(
                    text=f"Set your *trading pair* first with\n"
                         f"{lbl.SETTINGS} `-->` {lbl.PAIR}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboard_main())

                return ConversationHandler.END

            return func(self, bot, update, **kwargs)
        return _check_pair

    # Decorator to check if API keys are set
    @classmethod
    def check_keys(cls, func):
        def _check_keys(self, bot, update, **kwargs):
            if "data" not in kwargs or not kwargs["data"]:
                user_id = update.effective_user.id
                kwargs["data"] = self.db.get_user_data(user_id)

            if not kwargs["data"].api_key or not kwargs["data"].api_secret:
                update.message.reply_text(
                    text=f"Set your *API keys* first with\n"
                         f"{lbl.SETTINGS} `-->` {lbl.API_KEYS}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboard_main())

                return ConversationHandler.END

            return func(self, bot, update, **kwargs)
        return _check_keys

    @classmethod
    def back(cls, bot, update):
        update.message.reply_text(
            text=f"{emo.CANCEL} Canceled...",
            reply_markup=cls.keyboard_main())

        return ConversationHandler.END

    @classmethod
    def build_menu(cls, buttons, n_cols=1, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)

        return menu

    @classmethod
    def keyboard_main(cls):
        buttons = [
            KeyboardButton(lbl.TRADE),
            KeyboardButton(lbl.BALANCE),
            KeyboardButton(lbl.ORDERS),
            KeyboardButton(lbl.TICKER),
            KeyboardButton(lbl.TRADES),
            KeyboardButton(lbl.CHART),
            KeyboardButton(lbl.STATS),
            KeyboardButton(lbl.SETTINGS),
            KeyboardButton(lbl.BOT)
        ]

        return ReplyKeyboardMarkup(cls.build_menu(buttons, n_cols=3), resize_keyboard=True)

    @classmethod
    def keyboard_back(cls):
        buttons = [
            KeyboardButton(lbl.BACK)
        ]

        return ReplyKeyboardMarkup(cls.build_menu(buttons), resize_keyboard=True)

    @classmethod
    def trade_ogre_api_error(cls, response, update):
        if "success" not in response or response["success"]:
            return False

        error_msg = f"{emo.ERROR} {response['error']}"

        if update.message:
            update.message.reply_text(error_msg)
        else:
            update.callback_query.message.reply_text(error_msg)

        return True

    @staticmethod
    def trm_zro(value_to_trim, decimals=8):
        if isinstance(value_to_trim, float):
            return (("%." + str(decimals) + "f") % value_to_trim).rstrip("0").rstrip(".")
        elif isinstance(value_to_trim, str):
            str_list = value_to_trim.split(" ")
            for i in range(len(str_list)):
                old_str = str_list[i]
                if old_str.replace(".", "").replace(",", "").isdigit():
                    new_str = str((("%." + str(decimals) + "f") % float(old_str)).rstrip("0").rstrip("."))
                    str_list[i] = new_str
            return " ".join(str_list)
        else:
            return value_to_trim

    def get_handlers(self) -> List[Handler]:
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # TODO: Set expected return type
    def get_sequence(self):
        return Sequence.NORMAL


class Sequence(IntEnum):
    FIRST = auto()
    NORMAL = auto()
    LAST = auto()
