import os
import logging

from argparse import ArgumentParser
from tradeogrebot.database import Database
from tradeogrebot.telegrambot import TelegramBot
from tradeogrebot.config import ConfigManager as Cfg
from logging.handlers import TimedRotatingFileHandler


# TODO: LICENSE & README
# TODO: Manage requirements with 'pipenv'
# See: https://github.com/dvf/blockchain
# See: http://andrewsforge.com/article/python-new-package-landscape
class TradeOgreBot:

    def __init__(self):
        # Parse command line arguments
        self.args = self._parse_args()

        # Load config file
        Cfg(self.args.config)

        # Set up logging
        log_path = self.args.logfile
        log_level = self.args.loglevel
        self._init_logger(log_path, log_level)

        # Prepare database
        sql_path = "sql"
        db_path = self.args.database
        password = input("Enter DB password: ")

        # Create 'data' directory if not present
        data_path = os.path.dirname(db_path)
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        # Create database
        self.db = Database(password, db_path, sql_path)

        # Create bot
        bot_token = self._get_bot_token()
        self.tg = TelegramBot(bot_token, self.db)

    # Parse arguments
    def _parse_args(self):
        parser = ArgumentParser(description="Trade on TradeOgre with Telegram")

        # Config file
        parser.add_argument(
            "-cfg",
            dest="config",
            help="path to config file",
            default="config/config.json",
            required=False,
            metavar="FILE")

        # Save logfile
        parser.add_argument(
            "--no-logfile",
            dest="savelog",
            action="store_false",
            help="don't save logs to file",
            required=False)
        parser.set_defaults(savelog=True)

        # Logfile
        parser.add_argument(
            "-log",
            dest="logfile",
            help="path to logfile",
            default="log/tradeogrebot.log",
            required=False,
            metavar="FILE")

        # Log level
        parser.add_argument(
            "-lvl",
            dest="loglevel",
            type=int,
            choices=[0, 10, 20, 30, 40, 50],
            help="Disabled, Debug, Info, Warning, Error, Critical",
            default=30,
            required=False)

        # Database
        parser.add_argument(
            "-db",
            dest="database",
            help="path to SQLite database file",
            default="data/data.db",
            required=False,
            metavar="FILE")

        # Bot token
        parser.add_argument(
            "-tkn",
            dest="token",
            help="Telegram bot token",
            required=False,
            default=None)

        # Webhook
        parser.add_argument(
            "--webhook",
            dest="webhook",
            action="store_true",
            help="use webhook instead of polling",
            required=False)
        parser.set_defaults(webhook=False)

        return parser.parse_args()

    # Configure logging
    def _init_logger(self, logfile, level):
        logger = logging.getLogger()
        logger.setLevel(level)

        log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

        # Log to console
        console_log = logging.StreamHandler()
        console_log.setFormatter(logging.Formatter(log_format))
        console_log.setLevel(level)

        logger.addHandler(console_log)

        # Save logs if enabled
        if self.args.savelog:
            # Create 'log' directory if not present
            log_path = os.path.dirname(logfile)
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            file_log = TimedRotatingFileHandler(
                logfile,
                when="H",
                encoding="utf-8")

            file_log.setFormatter(logging.Formatter(log_format))
            file_log.setLevel(level)

            logger.addHandler(file_log)

    # Read bot token from file
    def _get_bot_token(self):
        if self.args.token:
            return self.args.token

        token_path = "config/bot.token"
        if os.path.isfile(token_path):
            with open(token_path, 'r') as file:
                return file.read().splitlines()[0]
        else:
            exit(f"ERROR: No token file '{token_path}' found")

    def start(self):
        if self.args.webhook:
            self.tg.bot_start_webhook()
        else:
            self.tg.bot_start_polling()

        self.tg.bot_idle()


if __name__ == '__main__':
    TradeOgreBot().start()
