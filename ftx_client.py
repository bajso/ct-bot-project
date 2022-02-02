import pandas as pd
import requests

FTX_URL = 'https://ftx.com/api'


def get_ftx_market_data():

    index_tickers = ['PRIV-PERP', 'ALT-PERP', 'DEFI-PERP',
                     'SHIT-PERP', 'EXCH-PERP', 'MID-PERP']

    url = f'{FTX_URL}/markets'
    markets = requests.get(url).json()

    fd = pd.DataFrame(markets['result'])
    # only consider perpertual futures
    fd = fd[fd['type'] == 'future']
    fd = fd[fd['name'].str.contains('PERP')]
    # with volume > 5M USD per day
    fd.sort_values(by='volumeUsd24h', ascending=False, inplace=True)
    fd = fd[fd['volumeUsd24h'] > 5000000]
    fd = fd[['name', 'volumeUsd24h']]
    fd.columns = ['ticker', 'volume']
    # drop index tickers
    fd = fd[~fd['ticker'].isin(index_tickers)]

    fd.to_csv('ftx_data.csv', index=False)
    return fd
