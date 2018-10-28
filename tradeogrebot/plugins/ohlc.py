import io
import pandas as pd
import plotly.io as pio
import tradeogrebot.emoji as emo
import plotly.figure_factory as fif

from io import BytesIO
from telegram import ParseMode
from telegram.ext import CommandHandler
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.api.cryptocompare import CryptoCompare


# TODO: Add all the cool features from 'chart'
class Ohlc(TradeOgreBotPlugin):

    TIME_FRAME = 120  # Hours

    def get_handlers(self):
        return [self._get_ohlc_handler()]

    def _get_ohlc_handler(self):
        return CommandHandler("ohlc", self._ohlc)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _ohlc(self, bot, update, data):
        from_sy = data.pair.split("-")[0]
        to_sy = data.pair.split("-")[1]

        days = int((self.TIME_FRAME + 1) / 24)

        ohlcv = CryptoCompare().historical_ohlcv_hourly(to_sy, from_sy, self.TIME_FRAME)["Data"]

        if not ohlcv:
            update.message.reply_text(
                text=f"No OHLC data available for {to_sy} {emo.OH_NO}",
                parse_mode=ParseMode.MARKDOWN)
            return

        o = [value["open"] for value in ohlcv]
        h = [value["high"] for value in ohlcv]
        l = [value["low"] for value in ohlcv]
        c = [value["close"] for value in ohlcv]
        t = [value["time"] for value in ohlcv]

        fig = fif.create_candlestick(o, h, l, c, pd.to_datetime(t, unit='s'))
        fig['layout']['yaxis'].update(tickformat="0.4r")
        fig['layout'].update(title=f"Price of {to_sy} in {from_sy} for {days} days")

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='webp'))),
            parse_mode=ParseMode.MARKDOWN)
