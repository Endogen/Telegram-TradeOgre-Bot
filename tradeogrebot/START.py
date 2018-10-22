import os
import re
import logging

from tradeogrebot.database import Database
from tradeogrebot.telegrambot import TelegramBot
from tradeogrebot.config import ConfigManager as Cfg
from logging.handlers import TimedRotatingFileHandler


# TODO: LICENSE & README
# TODO: Manage requirements with 'pipenv'
# See: https://github.com/dvf/blockchain
# See: http://andrewsforge.com/article/python-new-package-landscape/
class TradeOgreBot:

    PATH_PREFIX = "../"

    def __init__(self):
        Cfg(f"{self.PATH_PREFIX}config/config.json")
        path = self.PATH_PREFIX + Cfg.get("logfile")
        self._init_logger(path, Cfg.get("log_level"))

        # Ask for password
        password = input("Enter DB password: ")

        # Create database instance
        db_path = self.PATH_PREFIX + Cfg.get("db_path")
        sql_folder = self.PATH_PREFIX + Cfg.get("sql_folder")
        self.db = Database(password, db_path, sql_folder)

        # Create python-telegram-bot instance
        bot_token = self._get_bot_token()
        read_timeout = Cfg.get("tg_read_timeout")
        connect_timeout = Cfg.get("tg_connect_timeout")
        self.tg = TelegramBot(bot_token, self.db, read_timeout, connect_timeout)

    # Configure logging
    def _init_logger(self, logfile, level):
        logger = logging.getLogger()

        log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        logging.basicConfig(format=log_format, level=level)

        handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1, encoding="utf-8")
        handler.setFormatter(logging.Formatter(log_format))
        handler.extMatch = re.compile(r"^\d{8}$")
        handler.suffix = "%Y%m%d"
        handler.setLevel(level)

        logger.addHandler(handler)

    # Read bot token from file
    def _get_bot_token(self):
        token_file = self.PATH_PREFIX + Cfg.get("bot_token_file")

        if os.path.isfile(token_file):
            with open(token_file, 'r') as file:
                return file.read().splitlines()[0]
        else:
            exit(f"ERROR: No key file '{token_file}' found")

    def start(self):
        self.tg.bot_start()
        self.tg.bot_idle()


if __name__ == '__main__':
    TradeOgreBot().start()
