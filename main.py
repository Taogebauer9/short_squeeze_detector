from components.finviz_stocks import FinvizStocks as fs
from components.indicators import ttm_squeeze
from components.api import ApiClient

import pandas as pd
import numpy as np
import time
import os


def main():
    config = {}
    with open('config.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=',1)
            config[key.strip()] = value.strip()
            
    finviz = fs(config['URL'])
    api = ApiClient(config['API_KEY'])
    length = int(config['LENGTH'])
    intervals = [int(char) for char in config['INTERVALS'].split(',')]

    # Get the symbols from the Finviz data
    symbols = finviz.data['Ticker']
    print(symbols)
    
    # Get the stock data for each symbol
    all_symbol_data = []
    for symbol in symbols:
        try:
            data = api.get_stock_data(symbol)
        except Exception as e:
            print("Ran out of API calls. Waiting 1 minute.")
            # time.sleep(60)
            # data = api.get_stock_data(symbol)
            break
        data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.drop(columns=['timestamp'], inplace=True)
        data.set_index('datetime', inplace=True)
        all_symbol_data.append(data)
        print(f"Processed {symbol}")
        
        
    # # Adjust the data for each interval
    # for set in all_symbol_data:
    #     data = set.copy()
    #     for interval in intervals:
    #         data = 



    # calculate the TTM Squeeze for each dataset

    # ttm_squeeze(data, length)

    for item in all_symbol_data:
        print(item.shape)
        print(item.head())
        print(item.tail())
    
    # data = ttm_squeeze(data, 20)
    # print(data)
    
    
if __name__ == '__main__':
    main()