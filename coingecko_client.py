import pandas as pd
import requests


class CoingeckoClient:

    _COINGECKO_URL = 'https://api.coingecko.com/api/v3'
    _ROGUE_TICKERS = ['Stox', 'CakeDAO', 'Clover', 'Compound Coin', 'Genesis Mana', 'ParadiseFi', 'Fitmin', 'Golden Ratio Token',
                      'Menlo One', 'One', 'One Hundred Coin', 'Hymnode', 'Kaiken Shiba', 'Rose', 'Rune', 'THORChain (ERC20)',
                      'San Diego Coin', 'TRON (BSC)', 'UNICORN Token', 'UNIVERSE', 'Rise Of Nebula', 'Rinnegan', 'UNIVERSE Project',
                      'Mercury', 'CoviCoin', 'IceCream Finance', 'Step Hero Soul', 'Step', 'AstroFarms', 'Leo', 'Alien Worlds (BSC)',
                      'AlphaCoin', 'PolyAlpha Finance', 'Atlas Cloud', 'Atlantis', 'Truebit Protocol']

    def get_coingecko_data(self) -> pd.DataFrame:

        url = f'{self._COINGECKO_URL}/coins/list'
        response = requests.get(url).json()

        cd = pd.DataFrame(response)
        cd.drop('id', axis=1, inplace=True)

        # drop rouge tickers
        cd = cd[~cd['name'].str.contains('Binance-Peg|Heco-Peg|Wormhole|Wrapped')]
        cd = cd[~cd['name'].isin(self._ROGUE_TICKERS)]

        cd.reset_index(drop=True, inplace=True)
        return cd
