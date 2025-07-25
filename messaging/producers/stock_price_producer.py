from kafka import KafkaProducer
import yfinance as yf 
import json, time
import pandas as pd
from datetime import datetime, timezone
from config.kafka_config import KAFKA_CONFIG



def get_sp500_symbols():
    url="https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df=pd.read_html(url)[0]
    return df['Symbol'].tolist()

producer = KafkaProducer(
    bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    **KAFKA_CONFIG["producer_config"]
)

SYMBOLS = get_sp500_symbols()[:50]

while True :

    try:
        print("🔍 Fetching stock prices for:", SYMBOLS)
        tickers = yf.Tickers(' '.join(SYMBOLS))

        for symbol in SYMBOLS:
            data = tickers.tickers[symbol].history(period='1d', interval='1m')

            if data.empty:
                print(f"⚠️ No data for {symbol}")
                continue

            current_price = data['Close'].iloc[-1]

            message = {
                "symbol": symbol,
                "price": round(current_price, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            producer.send(KAFKA_CONFIG["topics"]["stock_prices"], value=message)
            print(f"📤 Sent: {message}")
            with open("/home/saadyaq/SE/Python/finsentbot/data/raw/stock_prices.jsonl","a") as f:
                f.write(json.dumps(message) +'\n')
        print("✅ Sleeping 10 seconds...\n")
        time.sleep(10)

    except Exception as e :
        print(f"⚠️ Error: {e}")
        time.sleep(10)