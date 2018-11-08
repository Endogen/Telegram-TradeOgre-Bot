import tradeogrebot.labels as lbl

from telegram.ext import RegexHandler
from tradeogrebot.plugin import TradeOgreBotPlugin


class Back(TradeOgreBotPlugin):

    def get_handlers(self):
        return [self._get_back_handler()]

    def _get_back_handler(self):
        return RegexHandler(f"^({lbl.BACK})$", self.back)
