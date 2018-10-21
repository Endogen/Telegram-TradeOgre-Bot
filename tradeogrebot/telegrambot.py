import os
import logging
import importlib
import tradeogrebot.emoji as emo

from telegram import ParseMode
from telegram.ext import Updater
from telegram.error import InvalidToken
from tradeogrebot.plugin import TradeOgreBotPlugin


# TODO: Build main keyboard based on loaded plugins
# TODO: Internationalize strings
class TelegramBot:

    def __init__(self, bot_token, bot_db, read_timeout=10, connect_timeout=10):
        self.db = bot_db

        kwargs = dict()
        if read_timeout:
            kwargs["read_timeout"] = read_timeout
        if connect_timeout:
            kwargs["connect_timeout"] = connect_timeout

        try:
            self.updater = Updater(bot_token, request_kwargs=kwargs)
        except InvalidToken:
            exit("ERROR: Bot token not valid")

        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue

        self.load_plugins()

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self.handle_telegram_error)

    # Start the bot
    def bot_start(self):
        self.updater.start_polling(clean=True)

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def load_plugins(self):
        for _, _, files in os.walk("plugins"):
            for file in files:
                if not file.lower().endswith(".py"):
                    continue
                if file.startswith("_"):
                    continue

                module_name = file[:-3]
                module_path = f"plugins.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                    plugin_class = getattr(module, module_name.capitalize())
                    instance = plugin_class(self.updater, self.db)

                    if isinstance(instance, TradeOgreBotPlugin):
                        for handler in instance.get_handlers():
                            self.dispatcher.add_handler(handler)
                        logging.debug(f"Plugin '{module_name}' added")
                except Exception as ex:
                    msg = f"File '{file}' can't be loaded as a plugin: {ex}"
                    logging.warning(msg)

    # Handle all telegram and telegram.ext related errors
    def handle_telegram_error(self, bot, update, error):
        error_msg = f"{emo.ERROR} Telegram ERROR: *{error}*"
        logging.error(error)

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=TradeOgreBotPlugin.keyboard_main())
        else:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=TradeOgreBotPlugin.keyboard_main())
