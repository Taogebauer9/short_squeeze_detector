import pandas as pd
import numpy as np


def sma(series: pd.Series, length):
    return series.rolling(window=length, min_periods=1).mean()

def ema(series: pd.Series, length):
    return series.ewm(span=length, adjust=False).mean()

def stdev(series: pd.Series, length):
    return series.rolling(window=length, min_periods=1).std()

def highest(series: pd.Series, length):
    return series.rolling(window=length, min_periods=1).max()

def lowest(series: pd.Series, length):
    return series.rolling(window=length, min_periods=1).min()

def linreg(series, length) -> pd.Series:
    # Create a rolling window of matricies
    view = np.lib.stride_tricks.sliding_window_view(series, (length,))
    xxx=np.vstack([np.arange(length), np.ones(length)]).T
    roll_mat=(np.linalg.inv(xxx.T @ xxx) @ (xxx.T) @ view.T)[0]
    roll_mat = np.concatenate([np.full(length-1, np.nan), roll_mat])
    return roll_mat

def ttm_squeeze(data, length) -> pd.DataFrame:
    close = data['close']
    high = data['high']
    low = data['low']
    tr = data['high'] - data['low']  # True Range

    bband = sma(close, length) + 2 * stdev(close, length)
    keltner = ema(close, length) + ema(tr, length)

    e1 = (highest(high, length) + lowest(low, length)) / 2 + sma(close, length)
    osc = linreg(close - e1 / 2, length)
    diff = bband - keltner
    
    osc_key = f'osc_{length}'
    diff_key = f'diff_{length}'

    data[osc_key] = osc
    data[diff_key] = diff
    return data
    

if __name__ == "__main__":
    # Create random sample data
    np.random.seed(42)  # for reproducibility
    base = np.random.randn(1000).cumsum()  # random walk
    
    data = pd.DataFrame({
        'close': base,
        'high': base + abs(np.random.randn(1000)),  # high is always above close
        'low': base - abs(np.random.randn(1000))    # low is always below close
    })
    
    # Check if there are any NaN values in the results
    print(np.isnan(sma(data['close'], 20)).any())
    print(np.isnan(ema(data['close'], 20)).any())
    print(np.isnan(stdev(data['close'], 20)).any())
    print(np.isnan(highest(data['close'], 20)).any())
    print(np.isnan(lowest(data['close'], 20)).any())
    
    # Test the TTMSqueeze indicator
    result = ttm_squeeze(data, 20)
    
    print("Last few rows of the result:")
    print(result.tail())