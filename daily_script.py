import pandas as pd

import coingecko_client
import ftx_client
import twitter_client


def merge_market_data(ftx_data, coingecko_data):

    ftx_data['symbol'] = ftx_data['ticker'].str.split('-').str[0].str.lower()

    merged = pd.merge(coingecko_data, ftx_data, on='symbol', how='inner')

    # exclude BTC and ETH as random tweets don't move them
    merged.drop(merged[merged['symbol'].isin(['btc', 'eth'])].index, inplace=True)

    merged.sort_values(by='volume', ascending=False, inplace=True)
    merged.reset_index(drop=True, inplace=True)
    merged.to_csv('data/market_data.csv', index=False)


if __name__ == '__main__':

    # check for twitter user changes
    twitter_client.user_lookup()

    # update market data
    ftx_data = ftx_client.get_ftx_market_data()
    coingecko_data = coingecko_client.get_coingecko_data()

    merge_market_data(ftx_data, coingecko_data)
