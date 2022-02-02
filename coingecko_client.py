import pandas as pd
import requests

COINGECKO_URL = 'https://api.coingecko.com/api/v3'


rogue_tickers = ['Stox', 'CakeDAO', 'Clover', 'Compound Coin', 'Genesis Mana', 'ParadiseFi',
                 'Fitmin', 'Golden Ratio Token', 'Menlo One', 'One', 'One Hundred Coin',
                 'Hymnode', 'Kaiken Shiba', 'Rose', 'Rune', 'THORChain (ERC20)',
                 'San Diego Coin', 'TRON (BSC)', 'UNICORN Token', 'UNIVERSE', 'Rise Of Nebula',
                 'Rinnegan', 'UNIVERSE Project']


def get_coingecko_data():

    url = f'{COINGECKO_URL}/coins/list'
    response = requests.get(url).json()

    cd = pd.DataFrame(response)
    cd.drop('id', axis=1, inplace=True)

    # drop rouge tickers
    cd = cd[~cd['name'].str.contains('Binance-Peg|Wormhole|Wrapped')]
    cd = cd[~cd['name'].isin(rogue_tickers)]

    cd.reset_index(drop=True, inplace=True)
    cd.to_csv('data/coingecko_data.csv', index=False)
    return cd
