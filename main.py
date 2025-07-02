import os
from dotenv import load_dotenv

# Load .env BEFORE you try to use os.getenv
load_dotenv()

print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("CHAT_ID:", os.getenv("CHAT_ID"))

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

from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from websocket import WebSocketApp


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
def load_trades():
    try:
        with open("trades.json") as f:
            return json.load(f)
    except Exception:
        return []

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

def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)

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
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "entered": True,
        "activated_at": time.time()
    }
    trades.append(trade)
    save_trades(trades)
    send_message(
        f"✅ Trade activated for {symbol} {sig['side'].upper()}\n"
        f"Entry: `{sig['entry']}` | SL: `{sig['sl']}`\n"
        f"TP1: `{sig['tp1']}` | TP2: `{sig.get('tp2','')}` | TP3: `{sig.get('tp3','')}` | TP4: `{sig.get('tp4','')}`",
        user_id
    )

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
def best_intraday_signal_scan():
    strats = load_strategy()
    for symbol in SYMBOLS:
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

        closes_1h = [c["close"] for c in candles_1h[-21:]]
        closes_4h = [c["close"] for c in candles_4h[-21:]]
        ema1h = sum(closes_1h[-20:]) / 20
        ema4h = sum(closes_4h[-20:]) / 20
        price_1h = closes_1h[-1]
        price_4h = closes_4h[-1]

        # Decide side BEFORE scoring
        if price_1h > ema1h and price_4h > ema4h:
            side = "long"
        elif price_1h < ema1h and price_4h < ema4h:
            side = "short"
        else:
            logger.info(f"{symbol}: No clear trend on 1h/4h EMA, skipping.")
            continue

        score, conf, reasons = score_signal(symbol, candles_15m, candles_1h, candles_4h, side=side)

        if score < SCORE_THRESHOLD_MODERATE:
            logger.info(f"{symbol}: Score {score} < {SCORE_THRESHOLD_MODERATE}, skipping.")
            continue

        entry = get_realtime_price(symbol)
        if entry is None:
            logger.info(f"{symbol}: No real-time price, skipping.")
            continue

        # ==== STRICT HIGH-CONVICTION FILTER BLOCK ====
        closes_1h = [c["close"] for c in candles_1h[-21:]]
        closes_4h = [c["close"] for c in candles_4h[-21:]]
        ema1h = sum(closes_1h[-20:]) / 20
        ema4h = sum(closes_4h[-20:]) / 20
        price_1h = closes_1h[-1]
        price_4h = closes_4h[-1]

        # Decide side
        if price_1h > ema1h and price_4h > ema4h:
            side = "long"
        elif price_1h < ema1h and price_4h < ema4h:
            side = "short"
        else:
            logger.info(f"{symbol}: No clear trend on 1h/4h EMA, skipping.")
            continue
        score, conf, reasons = score_signal(symbol, candles_15m, candles_1h, candles_4h, side=side)
        recent_high = max([c["high"] for c in candles_15m[-24:]])
        recent_low = min([c["low"] for c in candles_15m[-24:]])
        last_vol = candles_15m[-1]["volume"]
        avg_vol = sum([c["volume"] for c in candles_15m[-10:]]) / 10
        macd_15 = get_macd_histogram(candles_15m)
        macd_1h = get_macd_histogram(candles_1h)

        if side == "long":
            if conf not in ["✅ STRONG", "⚠️ MODERATE"]:
                logger.info(f"{symbol}: Signal confidence {conf} not STRONG or MODERATE, skipping.")
                continue
            if "SMC High Confidence (15m)" not in reasons:
                logger.info(f"{symbol}: SMC High Confidence missing, skipping.")
                continue
            if last_vol <= 1.3 * avg_vol:
                logger.info(f"{symbol}: Volume spike not strong enough (last_vol={last_vol}, avg_vol={avg_vol}), skipping.")
                continue
            if entry <= recent_high:
                logger.info(f"{symbol}: Not breaking recent high ({entry} <= {recent_high}), skipping.")
                continue
            if macd_15 <= 0 or macd_1h <= 0:
                logger.info(f"{symbol}: MACD not both positive (15m={macd_15}, 1h={macd_1h}), skipping.")
                continue
            if not (price_1h > ema1h and price_4h > ema4h):
                logger.info(f"{symbol}: Not above EMA on 1h/4h (price_1h={price_1h}, ema1h={ema1h}, price_4h={price_4h}, ema4h={ema4h}), skipping.")
                continue

        if side == "short":
            if conf != "✅ STRONG":
                logger.info(f"{symbol}: Not STRONG signal ({conf}), skipping.")
                continue
            if "SMC High Confidence (15m)" not in reasons:
                logger.info(f"{symbol}: SMC High Confidence missing, skipping.")
                continue
            if last_vol <= 1.3 * avg_vol:
                logger.info(f"{symbol}: Volume spike not strong enough (last_vol={last_vol}, avg_vol={avg_vol}), skipping.")
                continue
            if entry >= recent_low:
                logger.info(f"{symbol}: Not breaking recent low ({entry} >= {recent_low}), skipping.")
                continue
            if macd_15 >= 0 or macd_1h >= 0:
                logger.info(f"{symbol}: MACD not both negative (15m={macd_15}, 1h={macd_1h}), skipping.")
                continue
            if not (price_1h < ema1h and price_4h < ema4h):
                logger.info(f"{symbol}: Not below EMA on 1h/4h (price_1h={price_1h}, ema1h={ema1h}, price_4h={price_4h}, ema4h={ema4h}), skipping.")
                continue
        # ==== END STRICT FILTER BLOCK ====

        atr = calculate_atr(candles_15m, 14)
        structure_lookback = 20

        if side == "long":
            swing_low = min(c["low"] for c in candles_15m[-structure_lookback:])
            sl_struct = swing_low
            sl_atr = entry - atr * 1.7
            sl_candidate = min(sl_struct, sl_atr)
            min_sl = entry * (1 - min_sl_pct)
            if sl_candidate < min_sl:
                sl = round(min_sl, 6)
                logger.info(f"{symbol}: SL moved up to min_sl_pct ({sl})")
            else:
                sl = round(sl_candidate, 6)
            risk = entry - sl
            if risk < max(entry * 0.002, 1.2 * atr):
                logger.info(f"{symbol}: Risk too small (risk={risk}, entry={entry}, atr={atr}), skipping.")
                continue
            tp1 = round(entry + risk * min_rr, 6)
            tp2 = round(entry + risk * max_rr, 6)
            min_tp = entry * (1 + min_tp_pct)
            if tp1 < min_tp:
                tp1 = round(min_tp, 6)
            if tp2 < tp1 + atr:
                tp2 = round(tp1 + atr, 6)
            resistances = sorted(set(c["high"] for c in candles_15m), reverse=False)
            tp3 = next((r for r in resistances if r > tp2), round(tp2 + atr, 6))
            tp4 = next((r for r in resistances if r > tp3), round(tp3 + atr, 6))
        else:
            swing_high = max(c["high"] for c in candles_15m[-structure_lookback:])
            sl_struct = swing_high
            sl_atr = entry + atr * 1.7
            sl_candidate = max(sl_struct, sl_atr)
            max_sl = entry * (1 + min_sl_pct)
            if sl_candidate > max_sl:
                sl = round(max_sl, 6)
                logger.info(f"{symbol}: SL moved down to max_sl_pct ({sl})")
            else:
                sl = round(sl_candidate, 6)
            risk = sl - entry
            if risk < max(entry * 0.002, 1.2 * atr):
                logger.info(f"{symbol}: Risk too small (risk={risk}, entry={entry}, atr={atr}), skipping.")
                continue
            tp1 = round(entry - risk * min_rr, 6)
            tp2 = round(entry - risk * max_rr, 6)
            min_tp = entry * (1 - min_tp_pct)
            if tp1 > min_tp:
                tp1 = round(min_tp, 6)
            if tp2 > tp1 - atr:
                tp2 = round(tp1 - atr, 6)
            supports = sorted(set(c["low"] for c in candles_15m), reverse=True)
            tp3 = next((s for s in supports if s < tp2), round(tp2 - atr, 6))
            tp4 = next((s for s in supports if s < tp3), round(tp3 - atr, 6))

        key = f"{symbol}_{side}"
        # --- Duplicate/cooldown filter ---
        rec_key = (symbol, side)
        now = time.time()
        prev = recent_signals.get(rec_key, {})
        is_same_signal = (
            prev and
            abs(prev.get("entry", 0) - entry) < 1e-4 and  # tiny float tolerance
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
        if not tp1_hit and tp1 is not None and (
            (side == "long" and price >= tp1) or (side == "short" and price <= tp1)):
            send_message(f"🥳 {symbol} {side.upper()} TP1 @ {price}", CHAT_ID)
            trade["tp1_hit"] = True
            changed = True
        # TP2
        if trade.get("tp1_hit") and not tp2_hit and tp2 is not None and (
            (side == "long" and price >= tp2) or (side == "short" and price <= tp2)):
            send_message(f"🏆 {symbol} {side.upper()} TP2 @ {price}", CHAT_ID)
            trade["tp2_hit"] = True
            changed = True
        # TP3
        if trade.get("tp2_hit") and not tp3_hit and tp3 is not None and (
            (side == "long" and price >= tp3) or (side == "short" and price <= tp3)):
            send_message(f"🏅 {symbol} {side.upper()} TP3 @ {price}", CHAT_ID)
            trade["tp3_hit"] = True
            changed = True
        # TP4 and close
        if trade.get("tp3_hit") and tp4 is not None and (
            (side == "long" and price >= tp4) or (side == "short" and price <= tp4)):
            send_message(f"🎯 {symbol} {side.upper()} TP4 @ {price}\nTrade completed!", CHAT_ID)
            trade["entered"] = False
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
            msg += (f"{t['symbol']} {t['side'].upper()}\n"
                    f"Entry: `{t['entry']}` | SL: `{t['sl']}`\n"
                    f"TP1: `{t.get('tp1','')}` {'✅' if t.get('tp1_hit') else '❌'}\n"
                    f"TP2: `{t.get('tp2','')}` {'✅' if t.get('tp2_hit') else '❌'}\n"
                    f"TP3: `{t.get('tp3','')}` {'✅' if t.get('tp3_hit') else '❌'}\n"
                    f"TP4: `{t.get('tp4','')}`\n\n")
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
            if not sdict.get("entered"):
                logger.info(f"Skipping {symbol}: not entered")
                continue
            side = sdict.get("side")
            candles_15m = get_candles(symbol, "15", 30)
            candles_1h = get_candles(symbol, "60", 30)
            candles_4h = get_candles(symbol, "240", 30)
            if len(candles_15m) < 21 or len(candles_1h) < 21 or len(candles_4h) < 21:
                logger.info(f"Skipping {symbol}: not enough candles")
                continue
            ema15 = sum([c["close"] for c in candles_15m[-20:]]) / 20
            ema1h = sum([c["close"] for c in candles_1h[-20:]]) / 20
            ema4h = sum([c["close"] for c in candles_4h[-20:]]) / 20
            price15 = candles_15m[-1]["close"]
            price1h = candles_1h[-1]["close"]
            price4h = candles_4h[-1]["close"]

            if price15 > ema15 and price1h > ema1h and price4h > ema4h:
                trend_now = "long"
            elif price15 < ema15 and price1h < ema1h and price4h < ema4h:
                trend_now = "short"
            else:
                trend_now = "neutral"

            last_trend = sdict.get("last_trend", None)
            logger.info(f"{symbol} entered:{sdict.get('entered')} side:{side} last_trend:{last_trend} → now:{trend_now}")

            # Only trigger alert if trade is active and trend has shifted away from side
            if last_trend is None:
                sdict["last_trend"] = trend_now
                changed = True
                continue
            if (side == "long" and trend_now != "long") or (side == "short" and trend_now != "short"):
                logger.warning(f"[TREND SHIFT] {symbol} {side.upper()} | last:{last_trend} now:{trend_now}")
                send_message(
                    f"⚠️ [TREND SHIFT] {symbol}: Trend changed for your {side.upper()}!\nPrev trend: {last_trend}, Now: {trend_now}\n→ Consider EXIT or tighten SL immediately!",
                    CHAT_ID
                )
                sdict["entered"] = False
                sdict["tp1_hit"] = False
                changed = True
            sdict["last_trend"] = trend_now
            strats[symbol] = sdict
        if changed:
            save_strategy(strats)
    except Exception as e:
        logger.exception(f"Error in check_trend_shift: {e}")

from flask import Flask, request

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
            try:
                entry = float(t['entry'])
                exit = float(
                    t.get('tp4') if exit_status == "TP4" else
                    t.get('tp3') if exit_status == "TP3" else
                    t.get('tp2') if exit_status == "TP2" else
                    t.get('sl')
                )
                pnl = f"{((exit - entry)/entry*100):.2f}%"
                if t['side'] == "short":
                    pnl = f"{((entry - exit)/entry*100):.2f}%"
            except:
                pass
            msg += (f"{t['symbol']} {t['side'].upper()} | Entry: `{t['entry']}` | "
                    f"Exit: `{exit_status}` | PnL: {pnl}\n")
        send_message(msg, chat_id)

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)

    # Handle normal messages
    if "message" in data:
        text = data["message"].get("text", "")
        chat_id = data["message"]["chat"]["id"]
        if text == "/start":
            send_message("🤖 Bot is online! Welcome!", chat_id)
        elif text in ("/trades", "/status"):
            handle_trades_command(chat_id)
        elif text == "/history":
            handle_history_command(chat_id)

    # Handle button clicks (callback_query)
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
             activate_trade(symbol, from_user)   # <--- CALL THE ACTUAL FUNCTION!

        elif cb_data.startswith("close_"):
            symbol = cb_data.replace("close_", "")
            send_message(f"❌ Trade closed for {symbol}", from_user)

        elif cb_data.startswith("breakeven_"):
            symbol = cb_data.replace("breakeven_", "")
            send_message(f"🟢 Breakeven set for {symbol}", from_user)

        elif cb_data.startswith("trail_"):
            symbol = cb_data.replace("trail_", "")
            send_message(f"🟠 Trailing SL enabled for {symbol}", from_user)
        elif cb_data.startswith("ignore_"):
            symbol = cb_data.replace("ignore_", "")
            send_message(f"⏸ Signal ignored for {symbol}", from_user)
        else:
            send_message(f"Unknown action: {cb_data}", from_user)


    return {"ok": True}, 200




# ... [Everything else: Flask app, WebSocket handlers, scheduling, etc. remain unchanged from your current code]

# ==== SCHEDULER & ENTRYPOINT ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # Start WebSocket in background thread
    threading.Thread(target=start_websocket, daemon=True).start()

    # Start scheduler jobs
    scheduler = BackgroundScheduler()
    scheduler.add_job(best_intraday_signal_scan, "interval", minutes=1)
    scheduler.add_job(check_trend_shift, "interval", minutes=1)
    scheduler.start()
    logger.info("Scheduled main intraday scan and trend shift check.")

    # Start Flask app (main thread)
    app.run(host="0.0.0.0", port=port)


