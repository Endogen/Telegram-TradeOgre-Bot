import io
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl
import tradeogrebot.constants as con

from io import BytesIO
from pandas import DataFrame
from telegram import ParseMode
from telegram.ext import RegexHandler, CommandHandler
from tradeogrebot.api.coingecko import CoinGecko
from tradeogrebot.plugin import TradeOgreBotPlugin


class Chart(TradeOgreBotPlugin):

    # Button label
    BTN_CHART = f"{emo.CHART} Chart"
    TIME_FRAME = 72  # Hours

    def get_handlers(self):
        return [self._get_chart_handler(), self._get_cmd_handler()]

    def _get_cmd_handler(self):
        return CommandHandler("chart", self._chart)

    def _get_chart_handler(self):
        return RegexHandler(f"^({lbl.CHART})$", self._chart)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.check_pair
    @TradeOgreBotPlugin.send_typing_action
    def _chart(self, bot, update, data):
        from_cur = data.pair.split("-")[0]
        to_cur = data.pair.split("-")[1]

        if not data.cg_coin_id:
            for coin in CoinGecko().get_coins_list():
                if coin["symbol"].lower() == to_cur.lower():
                    data.cg_coin_id = coin["id"]
                    break

        vs_cur = from_cur.lower()
        days = int(self.TIME_FRAME / 24)
        market_data = CoinGecko().get_coin_market_chart_by_id(data.cg_coin_id, vs_cur, days)

        # Volume
        df_volume = DataFrame(market_data["total_volumes"], columns=["DateTime", "Volume"])
        df_volume["DateTime"] = pd.to_datetime(df_volume["DateTime"], unit="ms")
        volume = go.Scatter(
            x=df_volume.get("DateTime"),
            y=df_volume.get("Volume"),
            name="Volume"
        )

        # Price
        df_price = DataFrame(market_data["prices"], columns=["DateTime", "Price"])
        df_price["DateTime"] = pd.to_datetime(df_price["DateTime"], unit="ms")
        price = go.Scatter(
            x=df_price.get("DateTime"),
            y=df_price.get("Price"),
            yaxis="y2",
            name="Price",
            line=dict(
                color=("rgb(22, 96, 167)"),
                width=2
            )
        )

        layout = go.Layout(
            images=[dict(
                source=f"{con.LOGO_URL_PARTIAL}{data.cmc_coin_id}.png",
                opacity=0.8,
                xref="paper", yref="paper",
                x=1.05, y=1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )],
            autosize=False,
            width=800,
            height=600,
            margin=go.layout.Margin(
                l=125,
                r=50,
                b=70,
                t=100,
                pad=4
            ),
            yaxis=dict(domain=[0, 0.20], ticksuffix="  "),
            yaxis2=dict(domain=[0.25, 1], ticksuffix="  "),
            title=f"{vs_cur.upper()} - {to_cur}",
            legend=dict(orientation="h", yanchor="top", xanchor="center", y=1.05, x=0.5),
            shapes=[{
                "type": "line",
                "xref": "paper",
                "yref": "y2",
                "x0": 0,
                "x1": 1,
                "y0": market_data["prices"][len(market_data["prices"]) - 1][1],
                "y1": market_data["prices"][len(market_data["prices"]) - 1][1],
                "line": {
                    "color": "rgb(50, 171, 96)",
                    "width": 1,
                    "dash": "dot"
                }
            }],
        )

        fig = go.Figure(data=[price, volume], layout=layout)
        fig["layout"]["yaxis2"].update(tickformat="0.8f")

        update.message.reply_photo(
            photo=io.BufferedReader(BytesIO(pio.to_image(fig, format="webp"))),
            parse_mode=ParseMode.MARKDOWN)
