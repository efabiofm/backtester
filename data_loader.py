import os
import ccxt
import pandas as pd
from datetime import timedelta

folder = "csv"
os.makedirs(folder, exist_ok=True)
data_file = os.path.join(folder, "btc_data_1h.csv")

def get_chart_data(start_date, end_date, timeframe):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file, parse_dates=['timestamp'], index_col='timestamp')
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        return df

    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    since = exchange.parse8601(f'{start_date}T00:00:00Z')
    until = exchange.parse8601(f'{end_date}T00:00:00Z')
    all_data = []

    while since < until:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not ohlcv:
            break
        df_temp = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'], unit='ms')
        all_data.append(df_temp)
        since = df_temp['timestamp'].iloc[-1] + timedelta(hours=1)
        if since >= pd.to_datetime(end_date):
            break
        since = int(since.timestamp() * 1000)

    df = pd.concat(all_data, ignore_index=True)
    df.set_index('timestamp', inplace=True)
    df.to_csv(data_file)

    return df
