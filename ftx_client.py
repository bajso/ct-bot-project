import os

import pandas as pd

from client import FtxClient as ftx_client


class FTXClient:

    _FTX_SECRETS_PATH = 'secrets/ftx.txt'

    def __init__(self) -> None:
        self._configure_client()

    def _configure_client(self) -> None:
        ftx_api_key, ftx_api_secret = '', ''
        if os.path.exists(self._FTX_SECRETS_PATH):
            with open(self._FTX_SECRETS_PATH, 'r', encoding='UTF8') as f:
                for line in f:
                    if 'api_key' in line:
                        ftx_api_key = line.split('=')[1].strip()
                    if 'api_secret' in line:
                        ftx_api_secret = line.split('=')[1].strip()

        if (not os.path.exists(self._FTX_SECRETS_PATH) or (ftx_api_key == '' and ftx_api_secret == '')):
            print("Configure FTX client")
            ftx_api_key = input("API KEY:")
            ftx_api_secret = input("API SECRET:")

        subaccount = input("Specify FTX subaccount or leave blank to use the main account:")

        response = None
        while response is None:
            try:
                client = ftx_client(ftx_api_key, ftx_api_secret, subaccount)
                response = client.get_account_info()
            except Exception as client_exception:
                print(f"Error occured: {client_exception}\n\nPlease try again ...")
                if 'subaccount' in str(client_exception):
                    subaccount = input("Specify FTX subaccount or leave blank to use the main account:")
                else:
                    ftx_api_key = input("API KEY:")
                    ftx_api_secret = input("API SECRET:")

        with open(self._FTX_SECRETS_PATH, 'w+', encoding='UTF8') as f:
            f.write(f"api_key={ftx_api_key}\n")
            f.write(f"api_secret={ftx_api_secret}")

        self._client = client

    def get_ftx_market_data(self) -> pd.DataFrame:
        index_tickers = ['PRIV-PERP', 'ALT-PERP', 'DEFI-PERP',
                         'SHIT-PERP', 'EXCH-PERP', 'MID-PERP']
        stables_tickers = ['USDT-PERP', 'CUSDT-PERP']

        markets = pd.DataFrame(self._client.list_markets())

        # only consider perpertual futures
        markets = markets[markets['type'] == 'future']
        markets = markets[markets['name'].str.contains('PERP')]
        # with volume > 5M USD per day
        markets.sort_values(by='volumeUsd24h', ascending=False, inplace=True)
        markets = markets[markets['volumeUsd24h'] > 5000000]
        markets = markets[['name', 'volumeUsd24h']]
        markets.columns = ['ticker', 'volume']
        # drop index and stables tickers
        markets = markets[~markets['ticker'].isin(index_tickers + stables_tickers)]
        # replace SHIB, SOS with their K* alternative (contract size limit)
        markets.replace({'SHIB-PERP': 'KSHIB-PERP', 'SOS-PERP': 'KSOS-PERP'}, inplace=True)
        markets.reset_index(drop=True, inplace=True)
        markets.to_csv('data/ftx_data.csv', index=False)

        return markets

    def place_order(self, ticker: str) -> None:
        print("TODO")
