import os
import logging
import importlib
import tradeogrebot.emoji as emo

from telegram import ParseMode
from telegram.ext import Updater
from telegram.error import InvalidToken
from tradeogrebot.plugin import Sequence
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.config import ConfigManager as Cfg


# TODO: Build main keyboard based on loaded plugins
# TODO: Internationalize strings
class TelegramBot:

    def __init__(self, bot_token, bot_db):
        self.db = bot_db
        self.token = bot_token

        read_timeout = Cfg.get("telegram", "read_timeout")
        connect_timeout = Cfg.get("telegram", "connect_timeout")

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
    def bot_start_polling(self):
        self.updater.start_polling(clean=True)

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def bot_start_webhook(self):
        self.updater.start_webhook(
            listen=Cfg.get("webhook", "listen"),
            port=Cfg.get("webhook", "port"),
            url_path=self.token,
            key=Cfg.get("webhook", "privkey_path"),
            cert=Cfg.get("webhook", "cert_path"),
            webhook_url=f"{Cfg.get('webhook', 'url')}:"
                        f"{Cfg.get('webhook', 'port')}/"
                        f"{self.token}")

    def load_plugins(self):
        for _, _, files in os.walk(os.path.join("tradeogrebot", "plugins")):
            plgns = [list() for seq in Sequence]

            try:
                for file in files:
                    if not file.lower().endswith(".py"):
                        continue
                    if file.startswith("_"):
                        continue

                    module_name = file[:-3]
                    module_path = f"tradeogrebot.plugins.{module_name}"

                    module = importlib.import_module(module_path)
                    plugin_class = getattr(module, module_name.capitalize())
                    inst = plugin_class(self.updater, self.db)

                    if isinstance(inst, TradeOgreBotPlugin):
                        plgns[inst.get_sequence().value - 1].append(inst)

                for lst in plgns:
                    for plgn in lst:
                        for handler in plgn.get_handlers():
                            self.dispatcher.add_handler(handler)

                        logging.info(f"Plugin '{type(plgn).__name__}' added")

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
