import csv
from TwitterAPI import TwitterAPI, TwitterOAuth

# API reference index https://developer.twitter.com/en/docs/twitter-api/api-reference-index
# API rate limits https://developer.twitter.com/en/docs/twitter-api/rate-limits

# Building search query https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
# Up to 512 characters long


user_lookup_url = 'users/by/username/:<username>'
user_timeline_url = 'users/:<id>/tweets'

o = TwitterOAuth.read_file('twitter_secrets.txt')
api = TwitterAPI(o.consumer_key, o.consumer_secret, o.access_token_key, o.access_token_secret, api_version='2')


def user_lookup():

    usernames = []
    with open('usernames.txt', 'r') as f:
        usernames = f.read().splitlines()

    user_data_list = []
    for u in usernames:
        r = api.request(user_lookup_url.replace('<username>', u))

        for item in r:
            user_data_list.append([item['id'], item['name'], item['username']])

        print(r.get_quota())

    with open('twitter_users.csv', 'w+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        headers = ['id', 'name', 'username']
        writer.writerow(headers)
        writer.writerows(user_data_list)


user_lookup()
