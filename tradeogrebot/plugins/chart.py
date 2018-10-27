import io
import plotly.io as pio
import plotly.figure_factory as fif
import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl

import plotly.graph_objs as go
import pandas as pd
from pandas import DataFrame

from io import BytesIO
from telegram import ParseMode
from telegram.ext import RegexHandler
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.api.coingecko import CoinGecko
from tradeogrebot.api.cryptocompare import CryptoCompare


class Chart(TradeOgreBotPlugin):

    # Button label
    BTN_CHART = f"{emo.CHART} Chart"
    TIME_FRAME = 71  # In hours

    def get_handlers(self):
        return [self._get_chart_handler()]

    def _get_chart_handler(self):
        return RegexHandler(f"^({lbl.BTN_CHART})$", self._chart)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _chart(self, bot, update, data):
        symbol = data.pair.split("-")[1]
        for coin in CoinGecko().get_coins_list():
            if coin["symbol"] == symbol.lower():
                coin_id = coin["id"]
                break

        days = 3
        vs_cur = "btc"
        market_data = CoinGecko().get_coin_market_chart_by_id(coin_id, vs_cur, days)

        # Volume

        # TODO: Do this as a Bar-Graph
        df_volume = DataFrame(market_data["total_volumes"], columns=["DateTime", "Volume"])
        df_volume['DateTime'] = pd.to_datetime(df_volume['DateTime'], unit='ms')
        volume = go.Scattergl(
            x=df_volume.get("DateTime"),
            y=df_volume.get("Volume"),
            name="Volume"
        )

        # Price
        df_price = DataFrame(market_data["prices"], columns=["DateTime", "Price"])
        df_price['DateTime'] = pd.to_datetime(df_price['DateTime'], unit='ms')
        price = go.Scattergl(
            x=df_price.get("DateTime"),
            y=df_price.get("Price"),
            yaxis="y2",
            name="Price",
            line=dict(
                color=('rgb(22, 96, 167)'),
                width=2
            )
        )

        title = f"Price of {symbol} in {vs_cur.upper()} for past {days} days"

        data = [price, volume]
        layout = go.Layout(
            yaxis=dict(domain=[0, 0.20]),
            yaxis2=dict(domain=[0.25, 1]),
            title=title,
            height=600,
            width=800,
            legend=dict(orientation='h', yanchor='top', xanchor='center', y=1, x=0.5),
            shapes=[{
                'type': 'line',
                'xref': 'paper',
                'yref': 'y2',
                'x0': 0,
                'x1': 1,
                'y0': market_data["prices"][len(market_data["prices"]) - 1][1],
                'y1': market_data["prices"][len(market_data["prices"]) - 1][1],
                'line': {
                    'color': 'rgb(50, 171, 96)',
                    'width': 1,
                    'dash': 'dot'
                }
            }],
        )

        fig = go.Figure(data=data, layout=layout)
        fig['layout']['yaxis2'].update(tickformat="0.8f")

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format='webp'))),
            parse_mode=ParseMode.MARKDOWN)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _chart_old(self, bot, update, data):
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
