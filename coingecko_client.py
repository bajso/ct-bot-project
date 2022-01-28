import requests
import pandas as pd

COINGECKO_URL = 'https://api.coingecko.com/api/v3'


def get_coingecko_coin_data():

    rouge_tickers = ['Stox', 'CakeDAO', 'Clover', 'Compound Coin', 'Genesis Mana', 'ParadiseFi',
                     'Fitmin', 'Golden Ratio Token', 'Menlo One', 'One', 'One Hundred Coin',
                     'Hymnode', 'Kaiken Shiba', 'Rose', 'Rune', 'THORChain (ERC20)',
                     'San Diego Coin', 'TRON (BSC)', 'UNICORN Token', 'UNIVERSE', 'Rise Of Nebula']

    url = f'{COINGECKO_URL}/coins/list'
    coingecko_data = requests.get(url).json()

    coins = pd.DataFrame(coingecko_data)
    coins.drop('id', axis=1, inplace=True)

    # read ftx market data csv
    ftx_data = pd.read_csv('ftx_market_data.csv')
    ftx_data['symbol'] = ftx_data['ticker'].str.split('-').str[0].str.lower()

    # merge datasets
    merged = pd.merge(coins, ftx_data, on='symbol', how='inner')

    # drop duplicates
    merged = merged[~merged['name'].str.contains('Binance-Peg|Wormhole|Wrapped')]
    merged = merged[~merged['name'].isin(rouge_tickers)]

    merged.sort_values(by='volume', ascending=False, inplace=True)
    merged.set_index('symbol', inplace=True)
    merged.to_csv('coingecko_data.csv')


get_coingecko_coin_data()
