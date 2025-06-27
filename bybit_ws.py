import json
from websocket import WebSocketApp
import threading

# === Shared price data store ===
price_data = {}

def on_message(ws, message):
    data = json.loads(message)
    if "data" in data and isinstance(data["data"], list):
        for item in data["data"]:
            symbol = item["symbol"]
            price = float(item["lastPrice"])
            price_data[symbol] = price
            print(f"[WebSocket] Live {symbol} Price: {price}")
            # TODO: Trigger strategy check here if needed

def on_error(ws, error):
    print(f"[WebSocket Error] {error}")

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket Closed]")

def on_open(ws):
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "OPUSDT"]
    args = [f"tickers.{sym}" for sym in symbols]
    payload = {
        "op": "subscribe",
        "args": args
    }
    ws.send(json.dumps(payload))
    print(f"[WebSocket Subscribed] {', '.join(symbols)}")

def run_ws():
    ws_url = "wss://stream.bybit.com/v5/public/linear"
    ws = WebSocketApp(ws_url,
                      on_open=on_open,
                      on_message=on_message,
                      on_error=on_error,
                      on_close=on_close)
    ws.run_forever()

def start_websocket():
    threading.Thread(target=run_ws, daemon=True).start()
