import pandas as pd
import requests

ftx_url = 'https://ftx.com/api'
output_file_name = 'ftx_market_data.csv'


def get_ftx_market_data():

    url = f'{ftx_url}/markets'
    markets = requests.get(url).json()

    df = pd.DataFrame(markets['result'])
    # only consider perpertual futures
    df = df[df['type'] == 'future']
    df = df[df['name'].str.contains('PERP')]
    # with volume > 5M USD per day
    df.sort_values(by='volumeUsd24h', ascending=False, inplace=True)
    df = df[df['volumeUsd24h'] > 5000000]
    df = df['volumeUsd24h']
    df.set_index('name', inplace=True)

    df.to_csv(output_file_name)


get_ftx_market_data()
