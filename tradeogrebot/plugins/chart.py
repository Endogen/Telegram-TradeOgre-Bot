import io
import pandas as pd
import plotly.io as pio
import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl

from io import BytesIO
from telegram import ParseMode
from telegram.ext import RegexHandler
from plotly.tools import FigureFactory as FiFa
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.api.cryptocompare import CryptoCompare


class Chart(TradeOgreBotPlugin):

    # Button label
    BTN_CHART = f"{emo.CHART} Chart"
    TIME_FRAME = 71

    def get_handlers(self):
        return [self.__get_chart_handler()]

    def __get_chart_handler(self):
        return RegexHandler(f"^({lbl.BTN_CHART})$", self.__chart)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def __chart(self, bot, update):
        user_id = update.message.from_user.id
        data = self.db.get_user_data(user_id)
        from_sy = data.pair.split("-")[0]
        to_sy = data.pair.split("-")[1]

        days = int((self.TIME_FRAME + 1) / 24)

        data = CryptoCompare().historical_ohlcv_hourly(to_sy, from_sy, self.TIME_FRAME)["Data"]

        o = [value["open"] for value in data]
        h = [value["high"] for value in data]
        l = [value["low"] for value in data]
        c = [value["close"] for value in data]
        t = [value["time"] for value in data]

        fig = FiFa.create_candlestick(o, h, l, c, pd.to_datetime(t, unit='s'))
        fig['layout']['yaxis'].update(tickformat="0.4r")
        fig['layout'].update(title=f"Price of {to_sy} in {from_sy} for {days} days")

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='webp'))),
            parse_mode=ParseMode.MARKDOWN)
