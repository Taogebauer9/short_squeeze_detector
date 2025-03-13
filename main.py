from components.finviz_stocks import FinvizStocks as fs
from components.indicators import ttm_squeeze
from components.api import ApiClient

import pandas as pd
import numpy as np
import time
import os


def main():
    pd.set_option('future.no_silent_downcasting', True)
    config = {}
    with open('config.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=',1)
            config[key.strip()] = value.strip()
            
    finviz = fs(config['URL'])
    api = ApiClient(config['API_KEY'])
    length = int(config['LENGTH'])
    intervals = config['INTERVALS'].split(',')

    # Get the symbols from the Finviz data
    symbols = finviz.data['Ticker']
    
    # Get the stock data for each symbol
    all_symbol_data = {}
    for symbol in symbols:
        try:
            data = api.get_stock_data(symbol)
        except Exception as e:
            print("Ran out of API calls. Waiting 1 minute.")
            time.sleep(60)
            data = api.get_stock_data(symbol)

        all_symbol_data[symbol] = format_stock_data(data)
        print(f"Processed {symbol}")
        
        
    # Check for squeeze status on every intreval for each symbol
    result = {}
    for symbol in symbols:
        data = all_symbol_data[symbol]
        for interval in intervals:
            data = resample_data(data, interval)
            data = ttm_squeeze(data, length)
            is_squeeze = any(data[f'diff_{length}'].tail(20) < 0)
            key = f"{symbol}_{interval}"
            result[key] = is_squeeze
            
    
    # Print results nicely grouped by symbol and interval
    for symbol in symbols:
        print(f"\n{symbol}:")
        for interval in intervals:
            key = f"{symbol}_{interval}"
            status = "In squeeze √" if result[key] else "In squeeze X"
            print(f"  {interval:<5}: {status}")


    
    
def format_stock_data(data):
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.drop(columns=['timestamp'], inplace=True)
    data.set_index('datetime', inplace=True)
    return data

def resample_data(data: pd.DataFrame, interval):
    # Create full date range at target frequency
    date_range = pd.date_range(start=data.index.min().floor(interval), 
                              end=data.index.max(),
                              freq=interval)
    
    # Filter out data outside of trading hours
    data = data.between_time('09:00', '16:00')
    
    # Resample and forward fill
    resampled = data.resample(interval).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
    resampled = resampled.reindex(date_range)
    resampled = resampled.ffill().infer_objects(copy=False)
    if resampled.index.freq != 'd':
        return resampled.between_time('09:00', '16:00')

    return resampled

    
if __name__ == '__main__':
    main()