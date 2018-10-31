import io
import threading
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import tradeogrebot.emoji as emo
import plotly.figure_factory as fif

from io import BytesIO
from telegram import ParseMode
from coinmarketcap import Market
from telegram.ext import CommandHandler
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.api.cryptocompare import CryptoCompare


# TODO: Add all the cool features from 'chart'
class Ohlc(TradeOgreBotPlugin):

    # Default time frame
    TIME_FRAME = 120  # Hours

    logo_url = str()
    symbol = str()

    def get_handlers(self):
        return [self._get_ohlc_handler()]

    def _get_ohlc_handler(self):
        return CommandHandler("ohlc", self._ohlc, pass_args=True)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _ohlc(self, bot, update, data, args):
        from_sy = data.pair.split("-")[0]
        to_sy = self.symbol = data.pair.split("-")[1]

        logo_thread = threading.Thread(target=self._get_coin_logo_url())
        logo_thread.start()

        if len(args) >= 1 and args[0].isnumeric() and args[0] != 0:
            self.TIME_FRAME = args[0]

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

        logo_thread.join()

        fig = fif.create_candlestick(o, h, l, c, pd.to_datetime(t, unit='s'))
        fig['layout']['yaxis'].update(tickformat="0.8f", ticksuffix="  ")
        fig['layout'].update(title=f"Price of {to_sy} in {from_sy}")
        fig['layout'].update(
            shapes=[{
                "type": "line",
                "xref": "paper",
                "yref": "y",
                "x0": 0,
                "x1": 1,
                "y0": c[len(c) - 1],
                "y1": c[len(c) - 1],
                "line": {
                    "color": "rgb(50, 171, 96)",
                    "width": 1,
                    "dash": "dot"
                }
            }])
        fig['layout'].update(
            autosize=False,
            width=800,
            height=600,
            margin=go.layout.Margin(
                l=125,
                r=50,
                b=70,
                t=100,
                pad=4
            ))
        fig['layout'].update(
            images=[dict(
                source=self.logo_url,
                opacity=0.8,
                xref="paper", yref="paper",
                x=1.05, y=1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )])

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='webp'))),
            parse_mode=ParseMode.MARKDOWN)

    def _get_coin_logo_url(self):
        listings = Market().listings()

        coin_id = None
        for listing in listings["data"]:
            if self.symbol.upper() == listing["symbol"].upper():
                coin_id = listing["id"]
                break

        self.logo_url = f"https://s2.coinmarketcap.com/static/img/coins/128x128/{coin_id}.png"
