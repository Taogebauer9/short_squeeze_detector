import pandas as pd
from datetime import datetime, timedelta
from polygon import RESTClient



class ApiClient:
    def __init__(self, api_key):
        self.client = RESTClient(api_key)

    def get_stock_data(self, ticker_symbol: str, multiplier=1) -> pd.DataFrame:
        # Just gets one year of data
        end = datetime.now()
        start = end - timedelta(days=365)

        aggs = self.client.list_aggs(
            ticker=ticker_symbol, 
            multiplier=multiplier, 
            timespan="minute", 
            from_=start.strftime('%Y-%m-%d'), 
            to=end.strftime('%Y-%m-%d'), 
            limit=50000
            )
        # Convert aggs to a list
        aggs_list = [agg for agg in aggs]
        
        # Convert the list to a DataFrame
        data = pd.DataFrame(aggs_list)
        
        return data



    
if __name__ == '__main__':
    api = ApiClient('psK8QMvhyWlZvCpkp2G8Dppn9pNyjXZZ')
    ticker_symbol = 'AAPL'
    period = '1y'
    data = api.get_stock_data(ticker_symbol, period, )
    print(data)