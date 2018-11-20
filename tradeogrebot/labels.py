import os
import gettext
import tradeogrebot.emoji as emo
import tradeogrebot.constants as con

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), con.LANG_DIR)
translate = gettext.translation('tradeogrebot', localedir, fallback=True)  # languages=["de"]
_ = translate.gettext

HELP = f"{emo.INFO} {_(Help & Info)}"
SHUTDOWN = f"{emo.FINISH} Shutdown"
REMOVE_AC = f"{emo.CANCEL} Remove Account"
FEEDBACK = f"{emo.SPEECH} Feedback"
TRADE = f"{emo.MONEY} Trade"
BALANCE = f"{emo.DIAMOND} Balance"
ORDERS = f"{emo.LIST} Orders"
TICKER = f"{emo.FLASH} Ticker"
TRADES = f"{emo.HANDSHAKE} Trades"
CHART = f"{emo.CHART} Chart"
STATS = f"{emo.STARS} Stats"
SETTINGS = f"{emo.COG} Settings"
BOT = f"{emo.ROBOT} Bot"
PAIR = f"{emo.LINK} Pair"
API_KEYS = f"{emo.KEY} API Keys"
BACK = f"{emo.BACK} Back"
NEXT = f"{emo.NEXT} Next"
BUY = f"{emo.BUY} Buy"
SELL = f"{emo.SELL} Sell"
P25 = "25%"
P50 = "50%"
P75 = "75%"
P100 = "100%"
YES = "Yes"
NO = "No"
