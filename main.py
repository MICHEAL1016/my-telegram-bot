import os
from dotenv import load_dotenv

# Load .env BEFORE you try to use os.getenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

import json
import time
import logging
import threading
import numpy as np
import pandas as pd
import requests
import mplfinance as mpf
last_signals = {}
recent_signals = {}
SIGNAL_COOLDOWN_SEC = 900
SL_COUNTER_FILE = "sl_counters.json"
# Global strict mode toggle
STRICT_LEVEL = 0  # Default to loose mode
STRICT_EMA = False
STRICT_SMC = False
STRICT_VOLUME = False
STRICT_MACD = False
STRICT_BREAKOUT = False
STRICT_OBTEST = False
STRICT_MULTI_TF = False
STRICT_RSI = False
STRICT_MIN_RR = False
STRICT_VOLATILITY = False
STRICT_NO_OVERLAP = False
STRICT_CONFIRMATION_BARS = False
STRICT_OB_RET = False
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from websocket import WebSocketApp
from datetime import datetime
BLACKLIST_FILE = "blacklist.json"
BLACKLIST_COOLDOWN = 3 * 60 * 60  # 3 hours
BLACKLIST_SL_LIMIT = 2
# ==== COIN SETTINGS ====
COIN_SETTINGS = {
    "BTCUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.004, "MIN_TP_PCT": 0.014},
    "ETHUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.005, "MIN_TP_PCT": 0.015},
    "BNBUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.005, "MIN_TP_PCT": 0.016},
    "SOLUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.006, "MIN_TP_PCT": 0.017},
    "XRPUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.007, "MIN_TP_PCT": 0.018},
    "DOGEUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "1000BONKUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.014, "MIN_TP_PCT": 0.03},
    "WIFUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "TRUMPUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.014, "MIN_TP_PCT": 0.03},
    "MOODENGUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.014, "MIN_TP_PCT": 0.03},
    "OPUSDT":   {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.01, "MIN_TP_PCT": 0.025},
    "ARBUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.025},
    "LINKUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.009, "MIN_TP_PCT": 0.021},
    "ADAUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.025},
    "MATICUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "APEUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.026},
    "SANDUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.026},
    "AXSUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "MANAUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "FTMUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "GALAUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.013, "MIN_TP_PCT": 0.028},
    "AAVEUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.009, "MIN_TP_PCT": 0.021},
    "CRVUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.024},
    "SUSHIUSDT":{"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.012, "MIN_TP_PCT": 0.025},
    "UNIUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.023},
    "COMPUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.023},
    "SNXUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.013, "MIN_TP_PCT": 0.028},
    "YFIUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.023},
    "LTCUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.007, "MIN_TP_PCT": 0.017},
    "BCHUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.008, "MIN_TP_PCT": 0.019},
    "DOTUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.01, "MIN_TP_PCT": 0.023},
    "ATOMUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.01, "MIN_TP_PCT": 0.023},
    "ETCUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.009, "MIN_TP_PCT": 0.021},
    "NEARUSDT": {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.013, "MIN_TP_PCT": 0.028},
    "FILUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.011, "MIN_TP_PCT": 0.024},
    "LRCUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.018, "MIN_TP_PCT": 0.036},
    "ZILUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.018, "MIN_TP_PCT": 0.036},
    "ENJUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "BATUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "ZRXUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "KNCUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "RENUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "BALUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "SXPUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "UMAUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "REPUSDT":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.02, "MIN_TP_PCT": 0.04},
    "default":  {"MIN_RR": 2.5, "MAX_RR": 3.5, "MIN_SL_PCT": 0.013, "MIN_TP_PCT": 0.026}
}


# ==== SIGNAL SCORING CONFIG ====
SIGNAL_WEIGHTS = {
    "smc_high": 2,
    "smc_ok": 1,
    "volume": 1,
    "reversal": 1,
    "rsi": 1,
    "macd": 1,
    "trend_alignment": 1
}
SCORE_THRESHOLD_STRONG = 4
SCORE_THRESHOLD_MODERATE = 2.5
SCORE_THRESHOLD_WEAK = 1.5

# ==== BOT CONFIG ====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"
STRAT_FILE = "strategies.json"
TRADES_FILE = "trades.json"
with open("symbols.json") as f:
    SYMBOLS = json.load(f)
active_signals = {}

# ==== LOGGING ====
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("TradeBot")

def save_trades(trades):
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)
def send_test_button():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": "Click the button below to test the callback!",
        "reply_markup": json.dumps({
            "inline_keyboard": [
                [
                    {"text": "Test Callback", "callback_data": "test_callback"}
                ]
            ]
        })
    }
    resp = requests.post(url, data=data)
    print(resp.text)
def load_sl_counters():
    try:
        with open(SL_COUNTER_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_sl_counters(counters):
    with open(SL_COUNTER_FILE, "w") as f:
        json.dump(counters, f, indent=2)
def handle_stop_loss(symbol):
    counters = load_sl_counters()
    counters[symbol] = counters.get(symbol, 0) + 1
    save_sl_counters(counters)

    # If SL limit hit, blacklist
    if counters[symbol] >= BLACKLIST_SL_LIMIT:
        blacklist_symbol(symbol)
        counters[symbol] = 0   # Reset after blacklisting
        save_sl_counters(counters)

def format_time(ts):
    """Convert Unix timestamp to readable time."""
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)
def load_blacklist():
    try:
        with open(BLACKLIST_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_blacklist(bl):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(bl, f, indent=2)

def is_blacklisted(symbol):
    bl = load_blacklist()
    ts = bl.get(symbol, 0)
    if time.time() < ts:
        return True
    return False

def update_blacklist_on_sl(symbol):
    trades = load_trades()
    # Last 5 closed trades for this symbol, count SLs
    sl_count = 0
    for t in reversed(trades):
        if t["symbol"] != symbol or t.get("entered", True):
            continue
        # Assume exit status is "SL" or manual close (not TPX)
        if "sl" in str(t.get("close_price", "")).lower() or t.get("exit_status", "") == "SL/Manual":
            sl_count += 1
        if sl_count >= BLACKLIST_SL_LIMIT:
            blacklist_symbol(symbol)
            logger.warning(f"{symbol} auto-blacklisted for {BLACKLIST_COOLDOWN/3600:.1f}h due to consecutive SLs.")
            return

# Call update_blacklist_on_sl(symbol) in your process_price_update STOP-LOSS logic, after each SL

# -------------- Order Block (OB) Detection --------------
def send_blacklist_alert(symbol, cooldown=BLACKLIST_COOLDOWN):
    hours = int(cooldown // 3600)
    minutes = int((cooldown % 3600) // 60)
    msg = (
        f"🚫 *{symbol}* auto-blacklisted after 2 consecutive SL hits.\n"
        f"No new signals will be sent for this coin for the next "
        f"{hours}h {minutes}m to protect your account."
    )
    send_message(msg, CHAT_ID)
def blacklist_symbol(symbol):
    # Load blacklist state
    try:
        with open(BLACKLIST_FILE) as f:
            bl = json.load(f)
    except Exception:
        bl = {}
    bl[symbol] = int(time.time()) + BLACKLIST_COOLDOWN
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(bl, f)
    send_blacklist_alert(symbol)  # <-- Telegram alert!

def detect_order_blocks(candles, side="long"):
    """
    Return a list of order block price levels from recent price action.
    For longs: find last swing down candle (big red) with volume spike and close near low (bullish OB)
    For shorts: last swing up candle (big green) with volume spike and close near high (bearish OB)
    """
    obs = []
    for i in range(len(candles)-6, len(candles)-1):  # last 5 candles
        c = candles[i]
        rng = c["high"] - c["low"]
        vol = c["volume"]
        # Heuristic: Order block = big candle, high volume, closes near wick extreme
        if side == "long" and c["close"] < c["open"] and (c["close"]-c["low"] < rng*0.25) and vol > np.mean([k["volume"] for k in candles[i-6:i+1]])*1.2:
            obs.append(c["low"])
        if side == "short" and c["close"] > c["open"] and (c["high"]-c["close"] < rng*0.25) and vol > np.mean([k["volume"] for k in candles[i-6:i+1]])*1.2:
            obs.append(c["high"])
    # Deduplicate, keep only unique, sorted
    return sorted(list(set(obs)))

# -------------- Retest Logic --------------
def is_retest(entry, ob_levels, side, tolerance=0.002):
    """
    Return True if entry is a retest (within tolerance%) of an order block zone
    """
    for ob in ob_levels:
        if side == "long" and abs(entry - ob) / entry <= tolerance:
            return True
        if side == "short" and abs(entry - ob) / entry <= tolerance:
            return True
    return False
def send_message(text, chat_id, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.warning(f"Telegram send_message failed: {e}")


def send_chart_image(filepath, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(filepath, "rb") as img:
        files = {"photo": img}
        data = {"chat_id": CHAT_ID, "caption": caption}
        requests.post(url, files=files, data=data)

def answer_callback_query(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    data = {"callback_query_id": callback_query_id}
    if text:
        data["text"] = text
    try:
        requests.post(url, json=data, timeout=5)  # use json=data here too
    except Exception as e:
        logger.warning(f"Failed to answer callback: {e}")

def send_signal_with_button(symbol, text, signal_details=None):
    button = {
        "inline_keyboard": [
            [
                {"text": "✅ Activate Trade", "callback_data": f"activate_{symbol}"},
                {"text": "❌ Close", "callback_data": f"close_{symbol}"},
            ],
            [
                {"text": "🟢 Breakeven", "callback_data": f"breakeven_{symbol}"},
                {"text": "🟠 Trail", "callback_data": f"trail_{symbol}"},
                {"text": "⏸ Ignore", "callback_data": f"ignore_{symbol}"},
            ],
        ]
    }
    send_message(text, CHAT_ID, reply_markup=button)
    # Store for activation on button click (add as much as you have for the trade)
    if signal_details:
        last_signals[symbol] = signal_details


# ==== File Persistence ====
def load_strategy():
    try:
        with open(STRAT_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_strategy(strats):
    with open(STRAT_FILE, "w") as f:
        json.dump(strats, f, indent=2)

def load_trades():
    try:
        with open(TRADES_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []
# ==== API Calls ====
def safe_request(method, url, **kwargs):
    delay = 1
    for i in range(5):
        try:
            res = requests.request(method, url, timeout=5, **kwargs)
            if res.status_code == 429:
                logger.warning("Rate-limited, retry in %ss", delay)
                time.sleep(delay)
                delay *= 2
                continue
            res.raise_for_status()
            return res
        except Exception:
            if i < 4:
                time.sleep(delay)
                delay *= 2
            else:
                logger.exception("REST call failed: %s %s", method, url)
    return None

def get_candles(symbol, interval, limit=50):
    url = (
        f"https://api.bybit.com/v5/market/kline"
        f"?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    )
    res = safe_request("GET", url)
    if not res:
        return []
    data = res.json().get("result", {}).get("list", [])
    return [
        {
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        }
        for c in data
    ]

def get_realtime_price(symbol):
    url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
    r = safe_request("GET", url)
    if not r:
        return None
    data = r.json()
    try:
        price = float(data["result"]["list"][0]["lastPrice"])
        return price
    except Exception:
        return None

# ==== Indicators ====
def calculate_atr(candles, period=14):
    trs = []
    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        close_prev = candles[i - 1]["close"]
        tr = max(high - low, abs(high - close_prev), abs(low - close_prev))
        trs.append(tr)
    if len(trs) < period:
        return sum(trs) / len(trs) if trs else 0
    else:
        return sum(trs[-period:]) / period

def get_rsi(candles, period=14):
    closes = pd.Series([c["close"] for c in candles])
    delta = closes.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) else 50

def get_macd_histogram(candles, fast=12, slow=26, signal=9):
    closes = pd.Series([c["close"] for c in candles])
    ema_fast = closes.ewm(span=fast, adjust=False).mean()
    ema_slow = closes.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return histogram.iloc[-1] if len(histogram) else 0

def ema(prices, period=200):
    if len(prices) < period:
        return np.mean(prices)
    weights = np.exp(np.linspace(-1.0, 0.0, period))
    weights /= weights.sum()
    a = np.convolve(prices, weights, mode="valid")
    return a[-1]

def passes_volume_filter(candles, lookback=15):
    if len(candles) < lookback + 1:
        return False
    last_vol = candles[-1]["volume"]
    avg_vol = sum(c["volume"] for c in candles[-lookback:]) / lookback
    return last_vol > avg_vol

# ==== Advanced Candle Patterns ====
def detect_reversal_candle(symbol, tf="15"):
    candles = get_candles(symbol, tf, 2)
    if len(candles) < 2:
        return None
    prev, curr = candles[-2], candles[-1]
    o, c = curr["open"], curr["close"]
    body = abs(c - o)
    rng = curr["high"] - curr["low"]
    uw = curr["high"] - max(o, c)
    lw = min(o, c) - curr["low"]
    if body < rng * 0.3 and uw > body * 2 and c < o:
        return "Shooting Star"
    if (
        prev["close"] > prev["open"]
        and c < o
        and o > prev["close"]
        and c < prev["open"]
    ):
        return "Bearish Engulfing"
    if uw > body * 2 and lw < body:
        return "Bearish Pin Bar"
    if body < rng * 0.3 and lw > body * 2 and c > o:
        return "Bullish Pin Bar"
    if (
        prev["close"] < prev["open"]
        and c > o
        and o < prev["close"]
        and c > prev["open"]

    ):
        return "Bullish Engulfing"
    if lw > body * 2 and uw < body:
        return "Bullish Pin Bar"
    return None
def trail_stop_loss(trade, trigger_price, symbol, mode="atr", atr_mult=1.0, pct_trail=0.015):
    """
    Move SL to a tighter value after TP1/TP2/TP3 hit.
    - mode="atr": SL trails by (ATR * atr_mult) from trigger_price
    - mode="pct": SL trails by (pct_trail * price) from trigger_price
    """
    side = trade["side"]
    if mode == "atr":
        atr = calculate_atr(get_candles(symbol, "15", 20), 14)
        if side == "long":
            new_sl = trigger_price - atr * atr_mult
        else:
            new_sl = trigger_price + atr * atr_mult
    else:  # percentage trail
        if side == "long":
            new_sl = trigger_price * (1 - pct_trail)
        else:
            new_sl = trigger_price * (1 + pct_trail)
    return round(new_sl, 6)

def activate_trade(symbol, user_id):
    sig = last_signals.get(symbol)
    if not sig:
        send_message(f"⚠️ No signal data to activate for {symbol}.", user_id)
        return

    trades = load_trades()
    # Don't activate if already active for this symbol/side
    for t in trades:
        if t["symbol"] == symbol and t.get("entered", False) and t["side"] == sig["side"]:
            send_message(f"Trade already active for {symbol} {sig['side']}.", user_id)
            return

    trade = {
        "symbol": symbol,
        "side": sig["side"],
        "entry": sig["entry"],
        "sl": sig["sl"],
        "tp1": sig["tp1"],
        "tp2": sig.get("tp2"),
        "tp3": sig.get("tp3"),
        "tp4": sig.get("tp4"),
        "result": "open",
        "strict_level": STRICT_LEVEL,
        "opened_at": time.time(),
        "closed_time": None,
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "tp4_hit": False,
        "entered": True,
        "remaining_volume": 1.0,
        "partial_exits": [],
        "realized_pnl": 0.0,
        "activated_at": time.time(),
        "user_id": user_id,
        # === NEW FIELDS for partials ===
        "volume": 1.0,             
        "realized_pnl": 0.0,        # sum of partial PnLs booked
        "partial_exits": [],        # list of dicts: {"tp": "TP1", "price": x, "volume": y, "pnl": z}
        "breakeven": False,
        "trail": False,
    }

    trades.append(trade)
    save_trades(trades)
    send_message(
        f"✅ Trade activated for {symbol} {sig['side'].upper()}\n"
        f"Entry: `{sig['entry']}` | SL: `{sig['sl']}`\n"
        f"TP1: `{sig['tp1']}` | TP2: `{sig.get('tp2','')}` | TP3: `{sig.get('tp3','')}` | TP4: `{sig.get('tp4','')}`",
        user_id
    )
def check_trades():
    trades = load_trades()
    for t in trades:
        if not t.get("entered", False):
            continue
        price = get_realtime_price(t["symbol"])
        # ---- STOP-LOSS hit ----
        if price is None:
            continue
        if t["side"] == "long" and price <= t["sl"]:
            close_trade(t["symbol"], t["side"], "loss", price)
            send_message(f"🚨 SL hit for {t['symbol']} {t['side']}. Trade closed.", t.get("user_id"))
        elif t["side"] == "short" and price >= t["sl"]:
            close_trade(t["symbol"], t["side"], "loss", price)
            send_message(f"🚨 SL hit for {t['symbol']} {t['side']}. Trade closed.", t.get("user_id"))
        # ---- TP1 hit ----
        elif t["side"] == "long" and price >= t["tp1"]:
            close_trade(t["symbol"], t["side"], "win", price)
            send_message(f"🎯 TP1 hit for {t['symbol']} {t['side']}. Trade closed as WIN.", t.get("user_id"))
        elif t["side"] == "short" and price <= t["tp1"]:
            close_trade(t["symbol"], t["side"], "win", price)
            send_message(f"🎯 TP1 hit for {t['symbol']} {t['side']}. Trade closed as WIN.", t.get("user_id"))

def close_trade(symbol, side, result, price=None):
    trades = load_trades()
    now = time.time()
    closed = False
    for t in trades:
        if t["symbol"] == symbol and t["side"] == side and t.get("entered", False):
            t["entered"] = False
            t["result"] = result  # "win" or "loss"
            t["closed_time"] = now
            if price is not None:
                t["close_price"] = price
            closed = True
    save_trades(trades)
    return closed  # Returns True if closed, else False

def detect_candle_patterns(symbol, tfs=["15", "60"]):
    allowed_tfs = {"15", "60", "240"}
    if isinstance(tfs, str):
        tfs = [tfs]
    tfs = [str(tf) for tf in tfs if str(tf) in allowed_tfs]
    if not tfs:
        return []
    results = []
    for tf in tfs:
        candles = get_candles(symbol, tf, 5)
        if len(candles) < 3:
            continue
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        patterns = []
        # Engulfing
        if (
            c2["close"] > c2["open"]
            and c3["close"] < c3["open"]
            and c3["open"] > c2["close"]
            and c3["close"] < c2["open"]
        ):
            patterns.append(f"Bearish Engulfing [{tf}m]")
        if (
            c2["close"] < c2["open"]
            and c3["close"] > c3["open"]
            and c3["open"] < c2["close"]
            and c3["close"] > c2["open"]
        ):
            patterns.append(f"Bullish Engulfing [{tf}m]")
        # Hammer/Doji
        body = abs(c3["close"] - c3["open"])
        rng = c3["high"] - c3["low"]
        if (
            body < rng * 0.25
            and abs(
                (c3["high"] - max(c3["close"], c3["open"]))
                - (min(c3["close"], c3["open"]) - c3["low"])
            )
            < rng * 0.1
        ):
            patterns.append(f"Doji [{tf}m]")
        if body < rng * 0.3 and min(c3["close"], c3["open"]) - c3["low"] > body * 2:
            patterns.append(f"Hammer [{tf}m]")
        # Stars
        if (
            c1["close"] < c1["open"]
            and c2["close"] > c2["open"]
            and c3["close"] > c3["open"]
            and c2["open"] > c1["close"]
            and c2["close"] < c3["open"]
        ):
            patterns.append(f"Morning Star [{tf}m]")
        if patterns:
            results.extend(patterns)
    return results

# ==== SMC Logic ====
def smc_scan(symbol, tf="15"):
    candles = get_candles(symbol, tf, 20)
    if len(candles) < 4:
        return None
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]
    bos = closes[-1] > max(highs[-4:-1]) or closes[-1] < min(lows[-4:-1])
    mss = (highs[-1] < highs[-2] and highs[-2] > highs[-3]) or (
        lows[-1] > lows[-2] and lows[-2] < lows[-3]
    )
    ob = abs(closes[-1] - highs[-1]) / (highs[-1] - lows[-1] + 1e-8) < 0.25
    cf = sum([bos, mss, ob])
    if cf >= 2:
        return {"bos": bos, "mss": mss, "ob": ob, "confidence": "✅ High"}
    return None

# ==== Trend (EMA) Logic ====
def get_ema_trend(symbol, tf="60", ema_period=20):
    candles = get_candles(symbol, tf, ema_period+2)
    if len(candles) < ema_period+2:
        return None
    closes = [c["close"] for c in candles]
    price = closes[-1]
    ema_val = sum(closes[-ema_period:]) / ema_period
    return "long" if price > ema_val else "short"

# ==== Signal Score & Filter (UPGRADED) ====
def score_signal(symbol, candles_15m, candles_1h, candles_4h, side):
    score = 0
    reasons = []
    max_score = 0

    # --- SMC ---
    smc = smc_scan(symbol, "15")
    if smc and smc.get("confidence") == "✅ High":
        score += SIGNAL_WEIGHTS["smc_high"]
        reasons.append("SMC High Confidence (15m)")
        max_score += SIGNAL_WEIGHTS["smc_high"]
    elif smc and smc.get("confidence"):
        score += SIGNAL_WEIGHTS["smc_ok"]
        reasons.append(f"SMC {smc.get('confidence')} (15m)")
        max_score += SIGNAL_WEIGHTS["smc_ok"]
    else:
        max_score += SIGNAL_WEIGHTS["smc_high"]

    # --- Volume Spike ---
    if passes_volume_filter(candles_15m):
        score += SIGNAL_WEIGHTS["volume"]
        reasons.append("Volume Spike (15m)")
    max_score += SIGNAL_WEIGHTS["volume"]

    # --- Reversal Candle ---
    rev = detect_reversal_candle(symbol, "15")
    if (side == "long" and rev and "Bullish" in rev) or (side == "short" and rev and "Bearish" in rev):
        score += SIGNAL_WEIGHTS["reversal"]
        reasons.append(f"Reversal Candle: {rev} (15m)")
    max_score += SIGNAL_WEIGHTS["reversal"]

    # --- RSI ---
    rsi = get_rsi(candles_15m)
    if side == "long" and rsi < 68:
        score += SIGNAL_WEIGHTS["rsi"]
        reasons.append(f"RSI OK: {rsi:.1f}")
    elif side == "short" and rsi > 32:
        score += SIGNAL_WEIGHTS["rsi"]
        reasons.append(f"RSI OK: {rsi:.1f}")
    max_score += SIGNAL_WEIGHTS["rsi"]

    # --- MACD ---
    macd_hist = get_macd_histogram(candles_1h)
    if (side == "long" and macd_hist > 0) or (side == "short" and macd_hist < 0):
        score += SIGNAL_WEIGHTS["macd"]
        reasons.append(f"MACD OK: {macd_hist:.3f}")
    max_score += SIGNAL_WEIGHTS["macd"]

    # --- Trend Alignment (1h/4h EMA) ---
    closes_1h = [c["close"] for c in candles_1h[-21:]]
    closes_4h = [c["close"] for c in candles_4h[-21:]]
    ema1h = sum(closes_1h[-20:]) / 20
    ema4h = sum(closes_4h[-20:]) / 20
    price_1h = closes_1h[-1]
    price_4h = closes_4h[-1]
    trend_ok = (side == "long" and price_1h > ema1h and price_4h > ema4h) or (side == "short" and price_1h < ema1h and price_4h < ema4h)
    if trend_ok:
        score += SIGNAL_WEIGHTS["trend_alignment"]
        reasons.append("Multi-TF EMA Trend Alignment")
    max_score += SIGNAL_WEIGHTS["trend_alignment"]

    # --- Normalize to 1-5 range ---
    if max_score == 0:  # fallback to avoid zero division
        norm_score = 1
    else:
        norm_score = 1 + 4 * (score / max_score)

    # --- Add Confidence Tag ---
    if norm_score >= SCORE_THRESHOLD_STRONG:
        conf = "✅ STRONG"
    elif norm_score >= SCORE_THRESHOLD_MODERATE:
        conf = "⚠️ MODERATE"
    else:
        conf = "❗️WEAK"

    return round(norm_score, 2), conf, reasons

# ==== Plotting ====
def plot_signal_chart(symbol, candles, entry=None, sl=None, tp1=None, tp2=None, tp3=None, tp4=None, side=None, filename="signal.png"):
    try:
        df = pd.DataFrame(candles)
        df.index = pd.to_datetime([pd.Timestamp.now() - pd.Timedelta(minutes=15*(len(df)-i-1)) for i in range(len(df))])
        addplots = []
        if entry:
            addplots.append(mpf.make_addplot([entry]*len(df), color='blue', width=2, linestyle='-.', label='Entry'))
        if sl:
            addplots.append(mpf.make_addplot([sl]*len(df), color='red', width=2, linestyle='--', label='SL'))
        if tp1:
            addplots.append(mpf.make_addplot([tp1]*len(df), color='green', width=1, linestyle='-', label='TP1'))
        if tp2:
            addplots.append(mpf.make_addplot([tp2]*len(df), color='orange', width=1, linestyle=':', label='TP2'))
        if tp3:
            addplots.append(mpf.make_addplot([tp3]*len(df), color='purple', width=1, linestyle='-.', label='TP3'))
        if tp4:
            addplots.append(mpf.make_addplot([tp4]*len(df), color='brown', width=1, linestyle=':', label='TP4'))
        mpf.plot(df, type='candle', style='charles', addplot=addplots,
                 title=f"{symbol} Signal", ylabel="Price", savefig=filename)
        return filename
    except Exception as e:
        logger.warning(f"Chart plotting failed for {symbol}: {e}")
        return None
STRICT_LEVEL = 0  # 0 = loose, 1 = moderate, 2 = strict

def update_strict_flags():
    global STRICT_LEVEL
    global STRICT_EMA, STRICT_SMC, STRICT_VOLUME, STRICT_MACD, STRICT_BREAKOUT, STRICT_OBTEST
    global STRICT_MULTI_TF, STRICT_RSI, STRICT_MIN_RR, STRICT_VOLATILITY, STRICT_NO_OVERLAP, STRICT_CONFIRMATION_BARS, STRICT_OB_RET

    if STRICT_LEVEL == 0:
        STRICT_EMA = STRICT_SMC = STRICT_VOLUME = STRICT_MACD = STRICT_BREAKOUT = STRICT_OBTEST = False
        STRICT_MULTI_TF = STRICT_RSI = STRICT_MIN_RR = STRICT_VOLATILITY = STRICT_NO_OVERLAP = STRICT_CONFIRMATION_BARS = STRICT_OB_RET = False
    elif STRICT_LEVEL == 1:
        STRICT_EMA = True
        STRICT_VOLUME = True
        STRICT_MULTI_TF = False
        STRICT_RSI = True
        STRICT_MIN_RR = False
        STRICT_VOLATILITY = False
        STRICT_NO_OVERLAP = False
        STRICT_CONFIRMATION_BARS = False
        STRICT_OB_RET = False
    elif STRICT_LEVEL == 2:
        STRICT_EMA = True
        STRICT_SMC = True
        STRICT_VOLUME = True
        STRICT_MACD = True
        STRICT_MULTI_TF = True
        STRICT_RSI = True
        STRICT_MIN_RR = True
        STRICT_VOLATILITY = True
        STRICT_NO_OVERLAP = True
        STRICT_CONFIRMATION_BARS = True
        STRICT_OB_RET = False
    elif STRICT_LEVEL >= 3:
        STRICT_EMA = True
        STRICT_SMC = True
        STRICT_VOLUME = True
        STRICT_MACD = True
        STRICT_BREAKOUT = True
        STRICT_OBTEST = True
        STRICT_MULTI_TF = True
        STRICT_RSI = True
        STRICT_MIN_RR = True
        STRICT_VOLATILITY = True
        STRICT_NO_OVERLAP = True
        STRICT_CONFIRMATION_BARS = True
        STRICT_OB_RET = True


def best_intraday_signal_scan():
    strats = load_strategy()
    for symbol in SYMBOLS:
        if is_blacklisted(symbol):
            logger.info(f"{symbol}: Blacklisted, skipping signal scan.")
            continue

        cs = COIN_SETTINGS.get(symbol, COIN_SETTINGS['default'])
        min_rr = cs['MIN_RR']
        max_rr = cs['MAX_RR']
        min_sl_pct = cs['MIN_SL_PCT']
        min_tp_pct = cs['MIN_TP_PCT']

        candles_15m = get_candles(symbol, "15", 50)
        candles_1h  = get_candles(symbol, "60", 50)
        candles_4h  = get_candles(symbol, "240", 50)
        if len(candles_15m) < 40 or len(candles_1h) < 40 or len(candles_4h) < 40:
            logger.info(f"{symbol}: Not enough candles, skipping.")
            continue

        closes_15m = [c["close"] for c in candles_15m[-21:]]
        closes_1h = [c["close"] for c in candles_1h[-21:]]
        closes_4h = [c["close"] for c in candles_4h[-21:]]
        ema15 = sum(closes_15m[-20:]) / 20
        ema1h = sum(closes_1h[-20:]) / 20
        ema4h = sum(closes_4h[-20:]) / 20

        # --- EMA trend agreement (strict or relaxed) ---
        if STRICT_EMA:
            ema_long = all(c["close"] > ema1h for c in candles_1h[-2:]) and all(c["close"] > ema4h for c in candles_4h[-2:])
            ema_short = all(c["close"] < ema1h for c in candles_1h[-2:]) and all(c["close"] < ema4h for c in candles_4h[-2:])
        else:
            ema_long = candles_1h[-1]["close"] > ema1h and candles_4h[-1]["close"] > ema4h
            ema_short = candles_1h[-1]["close"] < ema1h and candles_4h[-1]["close"] < ema4h

        if ema_long:
            side = "long"
        elif ema_short:
            side = "short"
        else:
            logger.info(f"{symbol}: EMA trend not confirmed, skipping.")
            continue

        # ===== STRICT LOGIC FILTERS =====

        # STRICT_MULTI_TF: Require 3/3 TFs agree (15m, 1h, 4h EMA)
        if STRICT_MULTI_TF:
            up = sum([
                closes_15m[-1] > ema15,
                closes_1h[-1] > ema1h,
                closes_4h[-1] > ema4h
            ])
            down = sum([
                closes_15m[-1] < ema15,
                closes_1h[-1] < ema1h,
                closes_4h[-1] < ema4h
            ])
            if side == "long" and up < 3:
                logger.info(f"{symbol}: STRICT_MULTI_TF not all UP, skipping.")
                continue
            if side == "short" and down < 3:
                logger.info(f"{symbol}: STRICT_MULTI_TF not all DOWN, skipping.")
                continue

        # STRICT_RSI: Enforce tighter bands
        if STRICT_RSI:
            rsi = get_rsi(candles_15m)
            if side == "long" and rsi > 65:
                logger.info(f"{symbol}: STRICT_RSI long, RSI {rsi:.1f} > 65, skipping.")
                continue
            if side == "short" and rsi < 35:
                logger.info(f"{symbol}: STRICT_RSI short, RSI {rsi:.1f} < 35, skipping.")
                continue

        # STRICT_MIN_RR: Force higher min RR (e.g. 3.0+)
        strict_min_rr = 3.0 if STRICT_MIN_RR else min_rr

        # STRICT_VOLATILITY: Require ATR above a threshold
        entry = get_realtime_price(symbol)
        if entry is None:
            logger.info(f"{symbol}: No real-time price, skipping.")
            continue
        if STRICT_VOLATILITY:
            atr = calculate_atr(candles_15m, 14)
            if atr < entry * 0.0015:
                logger.info(f"{symbol}: STRICT_VOLATILITY ATR too low, skipping.")
                continue

        # STRICT_NO_OVERLAP: Skip if open trade exists for symbol
        if STRICT_NO_OVERLAP:
            open_trades = [t for t in load_trades() if t["symbol"] == symbol and t.get("entered", False)]
            if open_trades:
                logger.info(f"{symbol}: STRICT_NO_OVERLAP - open trade exists, skipping.")
                continue

        # STRICT_CONFIRMATION_BARS: Require X closes above/below EMA
        if STRICT_CONFIRMATION_BARS:
            X = 3  # Change as needed
            confirm_closes = closes_15m[-X:]
            if side == "long":
                if not all(c > ema15 for c in confirm_closes):
                    logger.info(f"{symbol}: STRICT_CONFIRMATION_BARS not enough closes above EMA, skipping.")
                    continue
            else:
                if not all(c < ema15 for c in confirm_closes):
                    logger.info(f"{symbol}: STRICT_CONFIRMATION_BARS not enough closes below EMA, skipping.")
                    continue

        # STRICT_OB_RET: Require "perfect" order block retest (exact touch)
        ob_levels = detect_order_blocks(candles_15m, side=side)
        if STRICT_OB_RET:
            if not ob_levels or not any(abs(entry - ob) / entry < 1e-4 for ob in ob_levels):
                logger.info(f"{symbol}: STRICT_OB_RET: entry not perfect OB retest, skipping.")
                continue

        # ===== END STRICT LOGIC FILTERS =====

        # --- SCORE + SMC (relaxed or strict) ---
        score, conf, reasons = score_signal(symbol, candles_15m, candles_1h, candles_4h, side=side)
        smc = smc_scan(symbol, "15")
        if score < SCORE_THRESHOLD_MODERATE:
            logger.info(f"{symbol}: Score {score} < {SCORE_THRESHOLD_MODERATE}, skipping.")
            continue
        if STRICT_SMC:
            if not (smc and smc.get("bos") and smc.get("mss") and smc.get("ob")):
                logger.info(f"{symbol}: SMC not all confirmed (need BOS+MSS+OB), skipping.")
                continue
        else:
            if not (smc and (smc.get("bos") or smc.get("ob"))):
                logger.info(f"{symbol}: No BOS/OB SMC, skipping.")
                continue

        # --- OB retest (loose if not strict) ---
        ob_tol = 0.003 if STRICT_OBTEST else 0.005
        if not ob_levels:
            logger.info(f"{symbol}: No recent OB detected, skipping.")
            continue
        if not STRICT_OB_RET and not is_retest(entry, ob_levels, side, tolerance=ob_tol):
            logger.info(f"{symbol}: Entry is NOT a retest of OB, skipping.")
            continue

        # --- Volume spike (strict or relaxed) ---
        last_vol = candles_15m[-1]["volume"]
        avg_vol = sum([c["volume"] for c in candles_15m[-10:]]) / 10
        vol_factor = 1.3 if STRICT_VOLUME else 1.15
        if last_vol <= vol_factor * avg_vol:
            logger.info(f"{symbol}: Volume spike <{vol_factor}× avg, skipping.")
            continue

        # --- MACD ---
        macd_15 = get_macd_histogram(candles_15m)
        macd_1h = get_macd_histogram(candles_1h)
        logger.info(f"{symbol}: MACD 15m={macd_15:.4f}, 1h={macd_1h:.4f}")
        if STRICT_MACD:
            if side == "long" and (macd_15 <= 0.01 or macd_1h <= 0.01):
                logger.info(f"{symbol}: MACD not clearly positive, skipping.")
                continue
            if side == "short" and (macd_15 >= -0.01 or macd_1h >= -0.01):
                logger.info(f"{symbol}: MACD not clearly negative, skipping.")
                continue
        else:
            if side == "long" and macd_15 <= 0.01:
                logger.info(f"{symbol}: MACD 15m not positive, skipping.")
                continue
            if side == "short" and macd_15 >= -0.01:
                logger.info(f"{symbol}: MACD 15m not negative, skipping.")
                continue

        # --- BREAKOUT ---
        recent_high = max([c["high"] for c in candles_15m[-24:]])
        recent_low = min([c["low"] for c in candles_15m[-24:]])
        if STRICT_BREAKOUT:
            if side == "long" and candles_15m[-1]["close"] <= recent_high:
                logger.info(f"{symbol}: 15m close not above high, skipping.")
                continue
            if side == "short" and candles_15m[-1]["close"] >= recent_low:
                logger.info(f"{symbol}: 15m close not below low, skipping.")
                continue
        else:
            if side == "long" and entry <= recent_high * 1.001:
                logger.info(f"{symbol}: Entry not near recent high, skipping.")
                continue
            if side == "short" and entry >= recent_low * 0.999:
                logger.info(f"{symbol}: Entry not near recent low, skipping.")
                continue

        # --- STOP-LOSS & TP calculation ---
        atr = calculate_atr(candles_15m, 14)
        lookback = 20
        buffer = max(entry * 0.001, atr * 0.18)
        if side == "long":
            swing_low = min(c["low"] for c in candles_15m[-lookback:])
            sl_candidate = swing_low - buffer
            recent_lows = [c["low"] for c in candles_15m[-3:]]
            sl_final = min(sl_candidate, min(recent_lows) - buffer)
            min_sl = entry * (1 - min_sl_pct)
            sl = round(max(sl_final, min_sl), 6)
            risk = entry - sl
            if risk < max(entry * 0.002, 1.2 * atr):
                logger.info(f"{symbol}: Risk too small (risk={risk}, entry={entry}, atr={atr}), skipping.")
                continue
        else:
            swing_high = max(c["high"] for c in candles_15m[-lookback:])
            sl_candidate = swing_high + buffer
            recent_highs = [c["high"] for c in candles_15m[-3:]]
            sl_final = max(sl_candidate, max(recent_highs) + buffer)
            max_sl = entry * (1 + min_sl_pct)
            sl = round(min(sl_final, max_sl), 6)
            risk = sl - entry
            if risk < max(entry * 0.002, 1.2 * atr):
                logger.info(f"{symbol}: Risk too small (risk={risk}, entry={entry}, atr={atr}), skipping.")
                continue

        # --- TP1, TP2, TP3, TP4 ---
        # Use strict_min_rr if set by strict logic
        if side == "long":
            tp1 = round(entry + risk * strict_min_rr, 6)
            tp2 = round(entry + risk * max_rr, 6)
            resistances = sorted(set(c["high"] for c in candles_15m if c["high"] > tp2))
            tp3 = round(resistances[0], 6) if resistances else round(tp2 + atr, 6)
            tp4 = round(resistances[1], 6) if len(resistances) > 1 else round(tp3 + atr, 6)
        else:
            tp1 = round(entry - risk * strict_min_rr, 6)
            tp2 = round(entry - risk * max_rr, 6)
            supports = sorted(set(c["low"] for c in candles_15m if c["low"] < tp2), reverse=True)
            tp3 = round(supports[0], 6) if supports else round(tp2 - atr, 6)
            tp4 = round(supports[1], 6) if len(supports) > 1 else round(tp3 - atr, 6)

        # --- Duplicate/cooldown and activation logic here (unchanged) ---
        key = f"{symbol}_{side}"
        rec_key = (symbol, side)
        now = time.time()
        prev = recent_signals.get(rec_key, {})
        is_same_signal = (
            prev and
            abs(prev.get("entry", 0) - entry) < 1e-4 and
            prev.get("score") == score and
            (now - prev.get("ts", 0)) < SIGNAL_COOLDOWN_SEC
        )
        if is_same_signal:
            logger.info(f"{symbol}: Duplicate/cooldown filter, skipping signal.")
            continue
        if active_signals.get(key):
            logger.info(f"{symbol}: Signal already active, skipping.")
            continue

        prefix = "🚀 *STRONG* SIGNAL" if conf == "✅ STRONG" else "⚠️ *MODERATE* SIGNAL"
        msg = (
            f"{prefix} {symbol} *{side.upper()}*\n"
            f"*Score:* {score}/5 {conf}\n"
            f"Entry: `{entry}` | SL: `{sl}`\n"
            f"TP1: `{tp1}` | TP2: `{tp2}` | TP3: `{tp3}` | TP4: `{tp4}`\n"
            f"ATR: {atr:.4f} | RSI: {get_rsi(candles_15m):.1f}\n"
            f"*Reasons:* " + "; ".join([r for r in reasons if r])
        )
        send_signal_with_button(symbol, msg, signal_details={
            "side": side,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "tp4": tp4
        })
        chart_path = plot_signal_chart(
            symbol, candles_15m,
            entry=entry, sl=sl,
            tp1=tp1, tp2=tp2, tp3=tp3, tp4=tp4,
            side=side, filename=f"{symbol}_signal.png"
        )
        if chart_path:
            send_chart_image(chart_path, caption=f"{symbol} Signal Chart")
        active_signals[key] = True






# Call this update_blacklist_on_sl(symbol) in your process_price_update after SL
# Example (in your process_price_update, after setting entered=False for an SL):
#    update_blacklist_on_sl(symbol)

def process_price_update(symbol, price):
    trades = load_trades()
    changed = False
    for trade in trades:
        if trade["symbol"] != symbol or not trade.get("entered", False):
            continue
        side = trade["side"]
        sl = trade["sl"]
        tp1 = trade.get("tp1")
        tp2 = trade.get("tp2")
        tp3 = trade.get("tp3")
        tp4 = trade.get("tp4")
        tp1_hit = trade.get("tp1_hit", False)
        tp2_hit = trade.get("tp2_hit", False)
        tp3_hit = trade.get("tp3_hit", False)

        # STOP-LOSS
        if (side == "long" and price <= sl) or (side == "short" and price >= sl):
            send_message(f"💥 {symbol} {side.upper()} STOP‐LOSS @ {price}", CHAT_ID)
            trade["entered"] = False
            changed = True
            continue  # Trade is done

        # TP1
        # TP1 partial exit logic
        if not tp1_hit and tp1 is not None and (
            (side == "long" and price >= tp1) or (side == "short" and price <= tp1)):
            # Partial exit: close 25%
            partial_vol = 0.25 * trade.get("remaining_volume", 1.0)
            entry = float(trade["entry"])
            if side == "long":
                pnl = (price - entry) / entry * 100 * partial_vol
            else:
                pnl = (entry - price) / entry * 100 * partial_vol

            # Update trade object for partial exit
            trade["partial_exits"] = trade.get("partial_exits", [])
            trade["partial_exits"].append({
                "tp": "TP1",
                "price": price,
                "volume": partial_vol,
                "pnl": pnl
            })
            trade["realized_pnl"] = trade.get("realized_pnl", 0.0) + pnl
            trade["remaining_volume"] = trade.get("remaining_volume", 1.0) - partial_vol
            trade["tp1_hit"] = True

            # Move SL to breakeven
            trade["sl"] = trade["entry"]
            trade["breakeven"] = True

            send_message(
                f"🥳 {symbol} {side.upper()} TP1 @ {price} | +{partial_vol*100:.0f}% position closed\n"
                f"Realized PnL: {trade['realized_pnl']:.2f}% | Remaining: {trade['remaining_volume']*100:.0f}%\n"
                f"SL moved to breakeven ({trade['entry']})!",
                CHAT_ID
            )
            changed = True

        # TP2
        # TP2 partial exit logic
        if trade.get("tp1_hit") and not tp2_hit and tp2 is not None and (
            (side == "long" and price >= tp2) or (side == "short" and price <= tp2)):
            # Partial exit: close another 25%
            partial_vol = 0.25 * trade.get("remaining_volume", 1.0)  # 25% of *current* remaining
            entry = float(trade["entry"])
            if side == "long":
                pnl = (price - entry) / entry * 100 * partial_vol
            else:
                pnl = (entry - price) / entry * 100 * partial_vol

            # Record this partial exit
            trade["partial_exits"].append({
                "tp": "TP2",
                "price": price,
                "volume": partial_vol,
                "pnl": pnl
            })
            trade["realized_pnl"] = trade.get("realized_pnl", 0.0) + pnl
            trade["remaining_volume"] = trade.get("remaining_volume", 1.0) - partial_vol
            trade["tp2_hit"] = True

            # TRAIL stop-loss: move SL up (for long) or down (for short)
            atr = calculate_atr(get_candles(symbol, "15", 20), 14)
            if side == "long":
                new_sl = price - atr * 0.7  # e.g. trail by 70% ATR below TP2
            else:
                new_sl = price + atr * 0.7  # trail by 70% ATR above TP2
            trade["sl"] = round(new_sl, 6)
            trade["trail"] = True

            send_message(
                f"🏆 {symbol} {side.upper()} TP2 @ {price} | +{partial_vol*100:.0f}% closed\n"
                f"Realized PnL: {trade['realized_pnl']:.2f}% | Remaining: {trade['remaining_volume']*100:.0f}%\n"
                f"SL trailed to {trade['sl']}!",
                CHAT_ID
            )
            changed = True

        # TP3
        # TP3 partial exit logic
        if trade.get("tp2_hit") and not tp3_hit and tp3 is not None and (
            (side == "long" and price >= tp3) or (side == "short" and price <= tp3)):
            # Partial exit: close another 25% of remaining
            partial_vol = 0.25 * trade.get("remaining_volume", 1.0)
            entry = float(trade["entry"])
            if side == "long":
                pnl = (price - entry) / entry * 100 * partial_vol
            else:
                pnl = (entry - price) / entry * 100 * partial_vol

            trade["partial_exits"].append({
                "tp": "TP3",
                "price": price,
                "volume": partial_vol,
                "pnl": pnl
            })
            trade["realized_pnl"] = trade.get("realized_pnl", 0.0) + pnl
            trade["remaining_volume"] = trade.get("remaining_volume", 1.0) - partial_vol
            trade["tp3_hit"] = True

            # TRAIL SL again (even tighter)
            atr = calculate_atr(get_candles(symbol, "15", 20), 14)
            if side == "long":
                new_sl = price - atr * 0.5  # trail by 50% ATR below TP3
            else:
                new_sl = price + atr * 0.5  # trail by 50% ATR above TP3
            trade["sl"] = round(new_sl, 6)

            send_message(
                f"🏅 {symbol} {side.upper()} TP3 @ {price} | +{partial_vol*100:.0f}% closed\n"
                f"Realized PnL: {trade['realized_pnl']:.2f}% | Remaining: {trade['remaining_volume']*100:.0f}%\n"
                f"SL trailed to {trade['sl']}!",
                CHAT_ID
            )
            changed = True

        # TP4 and close
        # TP4 — Final full exit
        if trade.get("tp3_hit") and tp4 is not None and (
            (side == "long" and price >= tp4) or (side == "short" and price <= tp4)):
            # Close ALL remaining position
            final_vol = trade.get("remaining_volume", 1.0)
            entry = float(trade["entry"])
            if side == "long":
                pnl = (price - entry) / entry * 100 * final_vol
            else:
                pnl = (entry - price) / entry * 100 * final_vol

            trade["partial_exits"].append({
                "tp": "TP4",
                "price": price,
                "volume": final_vol,
                "pnl": pnl
            })
            trade["realized_pnl"] = trade.get("realized_pnl", 0.0) + pnl
            trade["remaining_volume"] = 0.0
            trade["entered"] = False

            send_message(
                f"🎯 {symbol} {side.upper()} TP4 @ {price} | 100% closed\n"
                f"Final Realized PnL: {trade['realized_pnl']:.2f}%\n"
                f"Trade completed!",
                CHAT_ID
            )
            changed = True

    if changed:
        save_trades(trades)
def handle_trades_command(chat_id):
    trades = load_trades()
    open_trades = [t for t in trades if t.get("entered", False)]
    if not open_trades:
        send_message("No open trades at the moment.", chat_id)
    else:
        msg = "*Open Trades:*\n"
        for t in open_trades:
            flags = []
            if t.get("breakeven"): flags.append("🟢 BE")
            if t.get("trail"): flags.append("🟠 Trail")
            if t.get("ignored"): flags.append("⏸ Ignored")
            state = " | ".join(flags) if flags else ""

            # Live PnL calc
            try:
                entry = float(t['entry'])
                side = t['side']
                cur_price = get_realtime_price(t['symbol'])
                if cur_price:
                    if side == "long":
                        pnl = (cur_price - entry) / entry * 100
                    else:
                        pnl = (entry - cur_price) / entry * 100
                    pnl_str = f"{pnl:+.2f}%"
                else:
                    pnl_str = "N/A"
            except Exception:
                pnl_str = "N/A"

            # --- Add history & AI advice ---
            hist = get_trade_history_stats(t['symbol'], t['side'])
            ai = get_live_trade_advice(
                t['symbol'], t['side'],
                float(t['entry']), float(t['sl']),
                float(t.get('tp1', 0)), float(t.get('tp2', 0)),
                float(t.get('tp3', 0)), float(t.get('tp4', 0))
            )

            msg += (
                f"{t['symbol']} {t['side'].upper()} {state}\n"
                f"Entry: `{t['entry']}` | SL: `{t['sl']}`\n"
                f"TP1: `{t.get('tp1','')}` {'✅' if t.get('tp1_hit') else '❌'}\n"
                f"TP2: `{t.get('tp2','')}` {'✅' if t.get('tp2_hit') else '❌'}\n"
                f"TP3: `{t.get('tp3','')}` {'✅' if t.get('tp3_hit') else '❌'}\n"
                f"TP4: `{t.get('tp4','')}`\n"
                f"Live PnL: *{pnl_str}*\n"
                f"📊 *History:* TP1: {hist['tp1']}%  TP2: {hist['tp2']}%  TP3: {hist['tp3']}%  SL: {hist['sl']}%  (out of {hist['n']})\n"
                f"🤖 *AI Advice:*\n{ai}\n"
                "\n"
            )
        send_message(msg, chat_id)






def on_ws_open(ws):
    sub = {"op": "subscribe", "args": [f"publicTrade.{s}" for s in SYMBOLS]}
    ws.send(json.dumps(sub))
    logger.info("Subscribed to: %s", sub["args"])

def on_ws_message(ws, message):
    try:
        msg = json.loads(message)
    except Exception:
        return
    topic = msg.get("topic", "")
    data = msg.get("data", [])
    if topic.startswith("publicTrade.") and isinstance(data, list):
        for t in data:
            try:
                sym = t.get("symbol") or t.get("s")
                price = t.get("price") or t.get("p")
                if sym and price is not None:
                    process_price_update(sym, float(price))
            except Exception:
                pass

def on_ws_error(ws, error):
    logger.error("WebSocket error: %s", error)

def on_ws_close(ws, code, msg):
    logger.warning("WebSocket closed (%s): %s", code, msg)
    time.sleep(5)
    start_websocket()

def start_websocket():
    ws = WebSocketApp(
        BYBIT_WS_URL,
        on_open=on_ws_open,
        on_message=on_ws_message,
        on_error=on_ws_error,
        on_close=on_ws_close,
    )
    threading.Thread(
        target=lambda: ws.run_forever(ping_interval=20, ping_timeout=10), daemon=True
    ).start()
    logger.info("WebSocket started")
def check_trend_shift():
    try:
        logger.info("Running check_trend_shift...")
        strats = load_strategy()
        changed = False
        for symbol, sdict in strats.items():
            # --- Extra logging for all trades ---
            logger.info(f"{symbol}: entered={sdict.get('entered')}, side={sdict.get('side')}, last_trend={sdict.get('last_trend')}")

            if not sdict.get("entered"):
                continue

            side = sdict.get("side")
            candles_15m = get_candles(symbol, "15", 30)
            candles_1h = get_candles(symbol, "60", 30)
            candles_4h = get_candles(symbol, "240", 30)
            if len(candles_15m) < 21 or len(candles_1h) < 21 or len(candles_4h) < 21:
                logger.info(f"Skipping {symbol}: not enough candles")
                continue

            # Calculate EMAs and price
            ema15 = sum([c["close"] for c in candles_15m[-20:]]) / 20
            ema1h = sum([c["close"] for c in candles_1h[-20:]]) / 20
            ema4h = sum([c["close"] for c in candles_4h[-20:]]) / 20
            price15 = candles_15m[-1]["close"]
            price1h = candles_1h[-1]["close"]
            price4h = candles_4h[-1]["close"]

            # --- Flexible trend detection: 2 out of 3 TF must agree ---
            up = sum([price15 > ema15, price1h > ema1h, price4h > ema4h])
            down = sum([price15 < ema15, price1h < ema1h, price4h < ema4h])

            if up >= 2:
                trend_now = "long"
            elif down >= 2:
                trend_now = "short"
            else:
                trend_now = "neutral"

            last_trend = sdict.get("last_trend", None)
            logger.info(f"{symbol}: SIDE={side} LAST_TREND={last_trend} NOW={trend_now} ENTERED={sdict.get('entered')}")

            # --- Alert if trend shifts away from trade direction ---
            if last_trend is None:
                logger.info(f"{symbol}: Initializing last_trend to {trend_now}")
                sdict["last_trend"] = trend_now
                changed = True
                continue

            if (side == "long" and trend_now != "long") or (side == "short" and trend_now != "short"):
                logger.warning(f"[TREND SHIFT] {symbol} {side.upper()} | last:{last_trend} now:{trend_now}")
                send_message(
                    f"⚠️ [TREND SHIFT] {symbol}: Trend changed for your {side.upper()}!\n"
                    f"Prev trend: {last_trend}, Now: {trend_now}\n"
                    f"→ Consider EXIT or tighten SL immediately!",
                    CHAT_ID
                )
                # Auto-disable trade if you want (remove below if you want only alerts)
                sdict["entered"] = False
                sdict["tp1_hit"] = False
                changed = True

            sdict["last_trend"] = trend_now
            strats[symbol] = sdict

        if changed:
            save_strategy(strats)
    except Exception as e:
        logger.exception(f"Error in check_trend_shift: {e}")


app = Flask(__name__)
def handle_history_command(chat_id):
    trades = load_trades()
    closed_trades = [t for t in trades if not t.get("entered", False)]
    if not closed_trades:
        send_message("No closed trades yet.", chat_id)
    else:
        msg = "*Closed Trades:*\n"
        for t in closed_trades[-10:]:  # show last 10
            exit_status = "TP4" if t.get("tp3_hit") else \
                          "TP3" if t.get("tp2_hit") else \
                          "TP2" if t.get("tp1_hit") else "SL/Manual"
            pnl = "N/A"
            close_price = t.get("close_price", "N/A")
            closed_time_raw = t.get("closed_time")
            closed_time = format_time(closed_time_raw)
            try:
                entry = float(t['entry'])
                close_price = float(t.get('close_price', entry))  # Use the recorded close price, fallback to entry if not present
                if t['side'] == "short":
                    pnl = f"{((entry - close_price) / entry * 100):.2f}%"
                else:
                    pnl = f"{((close_price - entry) / entry * 100):.2f}%"
            except:
                pnl = "N/A"

            # Add state/flags if present
            flags = []
            if t.get("breakeven"): flags.append("🟢 BE")
            if t.get("trail"): flags.append("🟠 Trail")
            if t.get("ignored"): flags.append("⏸ Ignored")
            state = " | ".join(flags) if flags else ""
            msg += (
                f"{t['symbol']} {t['side'].upper()} {state}\n"
                f"Entry: `{t['entry']}` | Exit: `{exit_status}` | Closed at: `{close_price}`\n"
                f"Close Time: `{closed_time}` | PnL: {pnl}\n"
                "\n"
            )
        send_message(msg, chat_id)

def send_daily_stats():
    trades = load_trades()
    today = datetime.now().date()
    day_trades = [t for t in trades if t.get("closed_time") and datetime.fromtimestamp(t["closed_time"]).date() == today]
    if not day_trades:
        send_message("No closed trades today.", CHAT_ID)
        return

    win = 0
    loss = 0
    total_pnl = 0
    for t in day_trades:
        try:
            entry = float(t['entry'])
            exit_status = "SL/Manual"
            close_price = float(t.get("close_price", 0))
            if t.get("tp3_hit"):
                exit_status = "TP3"
                pnl = ((float(t.get('tp3')) - entry) / entry) * 100 if t['side'] == "long" else ((entry - float(t.get('tp3'))) / entry) * 100
                win += 1
            elif t.get("tp2_hit"):
                exit_status = "TP2"
                pnl = ((float(t.get('tp2')) - entry) / entry) * 100 if t['side'] == "long" else ((entry - float(t.get('tp2'))) / entry) * 100
                win += 1
            elif t.get("tp1_hit"):
                exit_status = "TP1"
                pnl = ((float(t.get('tp1')) - entry) / entry) * 100 if t['side'] == "long" else ((entry - float(t.get('tp1'))) / entry) * 100
                win += 1
            else:
                pnl = ((close_price - entry) / entry) * 100 if t['side'] == "long" else ((entry - close_price) / entry) * 100
                loss += 1
            total_pnl += pnl
        except:
            pass

    total = win + loss
    winrate = (win / total) * 100 if total else 0

    msg = (
        f"📊 *Daily Trade Stats*\n"
        f"Date: {today}\n"
        f"Trades: {total}\n"
        f"Wins: {win}\n"
        f"Losses: {loss}\n"
        f"Winrate: {winrate:.1f}%\n"
        f"Total PnL: {total_pnl:+.2f}%\n"
    )
    send_message(msg, CHAT_ID)
def get_tp_sl_odds(symbol=None, side=None, last_n=100):
    """Compute TP1/TP2/TP3/TP4/SL hit rates from last N closed trades (optionally filter by symbol/side)"""
    trades = load_trades()
    # Only look at closed trades that have SL/TP flags set
    closed = [t for t in trades if not t.get("entered", True)]
    if symbol: closed = [t for t in closed if t["symbol"] == symbol]
    if side:   closed = [t for t in closed if t["side"] == side]
    closed = closed[-last_n:]  # most recent N

    if not closed:
        # Avoid divide by zero, fallback to 0.5 for all
        return (0.5, 0.5, 0.5, 0.5, 0.5)

    tp1 = sum(t.get("tp1_hit") for t in closed) / len(closed)
    tp2 = sum(t.get("tp2_hit") for t in closed) / len(closed)
    tp3 = sum(t.get("tp3_hit") for t in closed) / len(closed)
    tp4 = sum(t.get("tp4_hit") for t in closed) / len(closed)
    sl  = sum(t.get("sl_hit")  for t in closed) / len(closed)
    return (tp1, tp2, tp3, tp4, sl)
def get_trade_advice(symbol, side, entry, tp1, tp2, tp3, tp4, sl):
    # This should load your real trade history with TP/SL hit tracking
    history = load_trades()  # <-- You must implement this! (see below)
    same_signal_trades = [t for t in history if t["symbol"] == symbol and t["side"] == side]
    def pct_hit(key):
        if not same_signal_trades: return "N/A"
        return "{:.0f}%".format(100 * sum(1 for t in same_signal_trades if t.get(key)) / len(same_signal_trades))
    odds = (
        f"TP1: {pct_hit('tp1_hit')} | TP2: {pct_hit('tp2_hit')} | "
        f"TP3: {pct_hit('tp3_hit')} | TP4: {pct_hit('tp4_hit')} | SL: {pct_hit('sl_hit')}"
    )
    advice = f"🤖 *AI advice:*\n{odds}\n"
    # Extra suggestion logic
    if pct_hit('tp1_hit') != "N/A" and float(pct_hit('tp1_hit').replace('%','')) > 75:
        advice += "Odds good for TP1. Consider trailing after TP1!\n"
    elif pct_hit('sl_hit') != "N/A" and float(pct_hit('sl_hit').replace('%','')) > 20:
        advice += "⚠️ SL risk higher than usual—manage risk closely.\n"
    return advice
def get_trade_history_stats(symbol, side, N=100):
    # Load last N closed trades for symbol+side from your trade history
    trades = load_trades()
    closed = [t for t in trades if t['symbol']==symbol and t['side']==side and not t.get("entered")]
    recent = closed[-N:] if len(closed) > N else closed
    def pct(key):
        return int(100 * sum(1 for t in recent if t.get(key)) / len(recent)) if recent else 0
    return {
        'tp1': pct("tp1_hit"),
        'tp2': pct("tp2_hit"),
        'tp3': pct("tp3_hit"),
        'tp4': pct("tp4_hit"),
        'sl':  pct("stopped"),
        'n':   len(recent)
    }
def get_live_trade_advice(symbol, side, entry, sl, tp1, tp2, tp3, tp4):
    price = get_realtime_price(symbol)
    if not price:
        return "Live price unavailable."
    # Calculate distances
    if side == "long":
        to_tp1 = max(0, tp1 - price)
        to_tp2 = max(0, tp2 - price)
        to_tp3 = max(0, tp3 - price)
        to_sl = max(0, price - sl)
        dist = price - entry
        direction = price >= entry
    else:
        to_tp1 = max(0, price - tp1)
        to_tp2 = max(0, price - tp2)
        to_tp3 = max(0, price - tp3)
        to_sl = max(0, sl - price)
        dist = entry - price
        direction = price <= entry

    # Live indicators
    candles_15m = get_candles(symbol, "15", 40)
    rsi = get_rsi(candles_15m)
    atr = calculate_atr(candles_15m, 14)
    momentum = price - candles_15m[-2]["close"]  # Change over last 2 candles
    trend = "UP" if price > sum(c["close"] for c in candles_15m[-20:])/20 else "DOWN"
    momentum_str = "✅ strong" if abs(momentum) > atr*0.2 else "⚠️ weak"

    # Probabilities (quick and simple, not ML)
    tp1_chance = 70 + 15*(direction) + 5*(rsi > 60 if side=="long" else rsi < 40) + 5*(momentum > 0 if side=="long" else momentum < 0)
    tp2_chance = tp1_chance - 18
    tp3_chance = tp1_chance - 32
    sl_chance = 100 - tp1_chance  # Simplified, for clear display

    # Clamp to 5-95%
    def clamp(x): return max(5, min(95, x))
    tp1_chance = clamp(tp1_chance)
    tp2_chance = clamp(tp2_chance)
    tp3_chance = clamp(tp3_chance)
    sl_chance  = clamp(sl_chance)

    advice = (
        f"— *Price*: `{price}` (entry {entry})\n"
        f"— *Distance to TP1*: {to_tp1:.2f} | TP2: {to_tp2:.2f} | TP3: {to_tp3:.2f}\n"
        f"— *RSI*: {rsi:.1f} | *ATR*: {atr:.2f}\n"
        f"— *Momentum*: {momentum_str}\n"
        f"— *Trend*: {trend}\n"
        f"— *Live Probabilities:*\n"
        f"   TP1: *{tp1_chance}%*   TP2: *{tp2_chance}%*   TP3: *{tp3_chance}%*   SL: *{sl_chance}%*\n"
        f"*Advice:* {'Hold' if tp1_chance > sl_chance else 'Consider closing or tighten SL!'}"
    )
    return advice

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    logger.info("Webhook received from %s", request.remote_addr)
    logger.info("Headers: %s", dict(request.headers))
    logger.info("Data: %s", json.dumps(data))

    # ---- Handle normal messages (ONE block only) ----
    if "message" in data:
        text = data["message"].get("text", "")
        chat_id = data["message"]["chat"]["id"]

        if text == "/start":
            send_message("🤖 Bot is online! Welcome!", chat_id)
        elif text in ("/trades", "/status"):
            handle_trades_command(chat_id)
        elif text == "/history":
            handle_history_command(chat_id)
        elif text == "/stats":
            send_daily_stats()
        elif text.startswith("/strictmode"):
            global STRICT_LEVEL
            parts = text.strip().split()
            levels = {
                "loose": 0, "easy": 0,
                "mid": 1, "medium": 1,
                "strict": 2, "hard": 2,
                "max": 3, "hardcore": 3
            }
            if len(parts) > 1:
                lvl = parts[1].lower()
                if lvl.isdigit():
                    STRICT_LEVEL = int(lvl)
                elif lvl in levels:
                    STRICT_LEVEL = levels[lvl]
                else:
                    send_message(
                        "Usage: /strictmode [level]\nLevels: 0 (loose), 1 (medium), 2 (strict), 3 (max)",
                        chat_id)
                    return {"ok": True}, 200
                update_strict_flags()
                send_message(f"Strict mode level set to *{STRICT_LEVEL}*", chat_id)
            else:
                send_message(
                    f"Current strict level: *{STRICT_LEVEL}*\nUsage: /strictmode [0-3]",
                    chat_id)
            return {"ok": True}, 200

    # ---- Handle button clicks (callback_query) ----
    if "callback_query" in data:
        callback = data["callback_query"]
        cb_id = callback["id"]
        cb_data = callback["data"]
        from_user = callback["from"]["id"]

        # Always answer the callback, or the Telegram client will "spin"!
        answer_callback_query(cb_id, text=f"Button clicked: {cb_data}")

        # React to button, always send to `from_user`!
        if cb_data == "test_callback":
            send_message("Test callback received!", from_user)
        elif cb_data.startswith("activate_"):
            symbol = cb_data.replace("activate_", "")
            activate_trade(symbol, from_user)

            # Show advice for the just-activated trade
            trades = load_trades()
            t = next((x for x in trades if x["symbol"] == symbol and x.get("entered", False)), None)
            if t:
                hist = get_trade_history_stats(t['symbol'], t['side'])
                ai = get_live_trade_advice(
                    t['symbol'], t['side'],
                    float(t['entry']), float(t['sl']),
                    float(t.get('tp1', 0)), float(t.get('tp2', 0)),
                    float(t.get('tp3', 0)), float(t.get('tp4', 0))
                )
                advice_msg = (
                    f"📊 *History:* TP1: {hist['tp1']}%  TP2: {hist['tp2']}%  TP3: {hist['tp3']}%  SL: {hist['sl']}%  (out of {hist['n']})\n"
                    f"🤖 *AI Advice:*\n{ai}"
                )
                send_message(advice_msg, from_user)

        elif cb_data.startswith("close_"):
            symbol = cb_data.replace("close_", "")
            trades = load_trades()
            price = get_realtime_price(symbol)
            now = int(time.time())
            for t in trades:
                if t["symbol"] == symbol and t.get("entered", False):
                    t["entered"] = False
                    t["closed_time"] = now        # Save close time (Unix timestamp)
                    t["close_price"] = price     # Save close price (or None if price unavailable)
            save_trades(trades)
            send_message(f"❌ Trade closed for {symbol} at price {price} (time: {now})", from_user)

        elif cb_data.startswith("breakeven_"):
            symbol = cb_data.replace("breakeven_", "")
            trades = load_trades()
            for t in trades:
                if t["symbol"] == symbol and t.get("entered", False):
                    t["breakeven"] = True        # Save the breakeven flag
            save_trades(trades)
            send_message(f"🟢 Breakeven set for {symbol}", from_user)

        elif cb_data.startswith("trail_"):
            symbol = cb_data.replace("trail_", "")
            trades = load_trades()
            for t in trades:
                if t["symbol"] == symbol and t.get("entered", False):
                    t["trail"] = True            # Save the trailing SL flag
            save_trades(trades)
            send_message(f"🟠 Trailing SL enabled for {symbol}", from_user)

        elif cb_data.startswith("ignore_"):
            symbol = cb_data.replace("ignore_", "")
            trades = load_trades()
            for t in trades:
                if t["symbol"] == symbol and t.get("entered", False):
                    t["ignored"] = True          # Save the ignore flag
            save_trades(trades)
            send_message(f"⏸ Signal ignored for {symbol}", from_user)

        else:
            send_message(f"Unknown action: {cb_data}", from_user)

    return {"ok": True}, 200




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # Start WebSocket in background thread
    threading.Thread(target=start_websocket, daemon=True).start()

    # Start scheduler jobs
    scheduler = BackgroundScheduler()
    scheduler.add_job(best_intraday_signal_scan, "interval", minutes=1)
    scheduler.add_job(check_trend_shift, "interval", minutes=1)
    # --- Add scheduler job ---
    scheduler.add_job(send_daily_stats, "cron", hour=23, minute=0)  # Sends at 23:00 every day
    scheduler.add_job(check_trades, "interval", seconds=60)  # checks every 30s, change as needed

    scheduler.start()
    logger.info("Scheduled main intraday scan and trend shift check.")

    # Start Flask app (main thread)
    app.run(host="0.0.0.0", port=port)


