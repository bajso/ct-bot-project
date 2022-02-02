import pandas as pd

import coingecko_client
import ftx_client
import twitter_client


def merge_market_data(ftx_data, coingecko_data):

    ftx_data['symbol'] = ftx_data['ticker'].str.split('-').str[0].str.lower()

    merged = pd.merge(coingecko_data, ftx_data, on='symbol', how='inner')

    merged.sort_values(by='volume', ascending=False, inplace=True)
    merged.to_csv('market_data.csv', index=False)


if __name__ == '__main__':

    # check for twitter user changes
    twitter_client.user_lookup()

    # update market data
    ftx_data = ftx_client.get_ftx_market_data()
    coingecko_data = coingecko_client.get_coingecko_data()

    merge_market_data(ftx_data, coingecko_data)
