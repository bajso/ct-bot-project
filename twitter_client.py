import csv
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import List

import numpy as np
import pandas as pd
from TwitterAPI import (OAuthType, TwitterAPI, TwitterConnectionError,
                        TwitterOAuth, TwitterRequestError)

# API reference index https://developer.twitter.com/en/docs/twitter-api/api-reference-index
# API rate limits https://developer.twitter.com/en/docs/twitter-api/rate-limits

# Building search query
# https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
# Up to 512 characters long


class TwitterClient:

    _TWITTER_SECRETS_PATH = 'secrets/twitter.txt'
    _USERNAMES_PATH = 'data/usernames.txt'
    _USER_LOOKUP_URL = 'users/by/username/:<username>'
    _USER_TIMELINE_URL = 'users/:<id>/tweets'
    _STREAM_RULES_URL = 'tweets/search/stream/rules'
    _STREAM_URL = 'tweets/search/stream'

    def __init__(self) -> None:
        self._configure_client()

    def _configure_client(self) -> None:
        secrets = None
        if not os.path.exists(self._TWITTER_SECRETS_PATH):
            print("Configure Twitter client")
            self._write_credentials()

        try:
            secrets = TwitterOAuth.read_file(self._TWITTER_SECRETS_PATH)
            self._client = TwitterAPI(consumer_key=secrets.consumer_key,
                                      consumer_secret=secrets.consumer_secret,
                                      access_token_key=secrets.access_token_key,
                                      access_token_secret=secrets.access_token_secret,
                                      auth_type=OAuthType.OAUTH2,
                                      api_version='2')
        except Exception as client_exception:
            print(f"Error occurred: {client_exception}\n\nPlease try again ...")
            self._write_credentials()

    def _write_credentials(self) -> None:
        consumer_key = input("CONSUMER KEY:")
        consumer_secret = input("CONSUMER SECRET:")
        access_token_key = input("ACCESS TOKEN KEY:")
        access_token_secret = input("ACCESS TOKEN SECRET:")
        with open(self._TWITTER_SECRETS_PATH, 'w+', encoding='UTF8') as f:
            f.write(f"consumer_key={consumer_key}\n")
            f.write(f"consumer_secret={consumer_secret}\n")
            f.write(f"access_token_key={access_token_key}\n")
            f.write(f"access_token_secret={access_token_secret}")

    #
    # REST endpoints
    #

    def uid_lookup(self, username: str) -> str:
        r = self._client.request(self._USER_LOOKUP_URL.replace('<username>', username))
        print(f'[{r.status_code}] QUOTA: {r.get_quota()}\n')
        return str(r.json()['data']['id'])

    def uids_lookup(self, save_to_csv: bool = False) -> List:
        uids = []
        with open(self._USERNAMES_PATH, 'r', encoding='UTF8') as f:
            usernames = f.read().splitlines()

            for u in usernames:
                uids.append(self.uid_lookup(u))

        if save_to_csv:
            with open('data/twitter_users.csv', 'w+', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                headers = ['id', 'username']
                rows = np.transpose([uids, usernames])
                writer.writerow(headers)
                writer.writerows(rows)

    def get_timeline(self, twtr_id: str, from_in_seconds: int = 5) -> json:
        # only search for new tweets within last <from_in_seconds> seconds
        ts_now = datetime.now(timezone.utc)
        ts = (ts_now - timedelta(seconds=from_in_seconds)).isoformat(timespec='seconds')

        r = self._client.request(resource=self._USER_TIMELINE_URL.replace('<id>', str(twtr_id)),
                                 params={'start_time': f'{ts}'})

        print(f'[{r.status_code}] QUOTA: {r.get_quota()}\n')

        tweets = r.json()
        if tweets['meta']['result_count'] == 0:
            return []

        return tweets['data']

    #
    # Streaming endpoints
    #

    def configure_stream_rules(self, value: str) -> None:
        # only stream from tier10k (news aggregator acccount)
        r = self._client.request(resource=self._STREAM_RULES_URL, params={'add': [{'value': value}]})
        print(f'[{r.status_code}] RULE ADDED: {json.dumps(r.json(), indent=2)}\n')

    def get_stream_rules(self) -> None:
        r = self._client.request(resource=self._STREAM_RULES_URL, method_override='GET')
        print(f'[{r.status_code}] RULES: {json.dumps(r.json(), indent=2)}\n')

    def delete_stream_rule(self, rule_ids: List[str]) -> None:
        r = self._client.request(resource=self._STREAM_RULES_URL, params={'delete': {'ids': [*rule_ids]}})
        print(f'[{r.status_code}] RULES DELETED: {json.dumps(r.json(), indent=2)}\n')

    def start_stream(self) -> None:
        try:
            r = self._client.request(resource=self._STREAM_URL)
            print(f'[{r.status_code}] START...')
            if r.status_code != 200:
                exit()
            for item in r:
                print(json.dumps(item, indent=2))
        except KeyboardInterrupt:
            print('\nDone!')
        except TwitterRequestError as request_e:
            print(f'\n{request_e.status_code}')
            for msg in iter(request_e):
                print(msg)
        except TwitterConnectionError as connection_e:
            print(connection_e)
        except Exception as e:
            print(e)

    #
    # Utils
    #

    def parse_tweets(self, tweets: json, market_data: pd.DataFrame) -> List[str]:
        tickers = set()
        for twt in tweets:
            text = twt['text'].lower()
            # remove special symbols
            text = re.sub(r"[\([{})\].,&;$:/\"\']", "", text)
            # ensures only whole words are checked (e.g. exclude 'ar' in 'are')
            text = text.split()

            # check for matching symbols (e.g SOL)
            for index, row in market_data.iterrows():
                if row['symbol'] in text:
                    ticker = market_data.iloc[index]['ticker']
                    print(ticker)
                    tickers.add(ticker)

            # check for matching names (e.g Solana)
            for index, row in market_data.iterrows():
                if row['name'] in text:
                    ticker = market_data.iloc[index]['ticker']
                    print(ticker)
                    tickers.add(ticker)
