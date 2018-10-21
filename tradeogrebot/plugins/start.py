import tradeogrebot.emoji as emo

from telegram import ParseMode
from telegram.ext import CommandHandler
from tradeogrebot.plugin import TradeOgreBotPlugin


class Start(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_start_handler()]

    def _get_start_handler(self):
        return CommandHandler("start", self._start)

    @TradeOgreBotPlugin.add_user
    def _start(self, bot, update):
        update.message.reply_text(
            text=f"{emo.STARS} *Welcome to TradeOgre-Bot* {emo.STARS}",
            reply_markup=self.keyboard_main(),
            parse_mode=ParseMode.MARKDOWN)
