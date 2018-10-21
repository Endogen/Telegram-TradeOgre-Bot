from telegram import ParseMode
from telegram.ext import CommandHandler
from tradeogrebot.plugin import TradeOgreBotPlugin


class Reset(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_reset_handler()]

    def _get_reset_handler(self):
        return CommandHandler("reset", self._reset)

    def _reset(self, bot, update):
        update.message.reply_text(
            text=f"Keyboard reset...",
            reply_markup=self.keyboard_main(),
            parse_mode=ParseMode.MARKDOWN)
