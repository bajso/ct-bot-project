import pandas as pd
import requests

FTX_URL = 'https://ftx.com/api'


def get_ftx_market_data():

    index_tickers = ['PRIV-PERP', 'ALT-PERP', 'DEFI-PERP',
                     'SHIT-PERP', 'EXCH-PERP', 'MID-PERP']

    url = f'{FTX_URL}/markets'
    markets = requests.get(url).json()

    df = pd.DataFrame(markets['result'])
    # only consider perpertual futures
    df = df[df['type'] == 'future']
    df = df[df['name'].str.contains('PERP')]
    # with volume > 5M USD per day
    df.sort_values(by='volumeUsd24h', ascending=False, inplace=True)
    df = df[df['volumeUsd24h'] > 5000000]
    df = df[['name', 'volumeUsd24h']]
    df.columns = ['ticker', 'volume']
    df.set_index('ticker', inplace=True)
    # drop specific perpetuals
    df.drop(index_tickers, inplace=True, errors='ignore')

    df.to_csv('ftx_market_data.csv')


get_ftx_market_data()
