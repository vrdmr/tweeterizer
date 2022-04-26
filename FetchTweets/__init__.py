import functools
import json
import logging
import operator
import os
from datetime import datetime, timedelta

import azure.functions as func
import tweepy

from utils import dictify_tweet

FETCH_TWEETS_COUNT = 30
"""Fetch these many number of tweets"""

SEARCH_TERMS = ["PyCon", "Python", "Azure"]
TWITTER_CLIENT = tweepy.Client(os.environ.get("BEARER_TOKEN"))


def main(timer: func.TimerRequest) -> str:
    """Timer trigger running every hour"""

    recent_tweets = [
        TWITTER_CLIENT.search_recent_tweets(term, max_results=FETCH_TWEETS_COUNT).data
        for term in SEARCH_TERMS
    ]

    flattened_recent_tweets = functools.reduce(operator.iconcat, recent_tweets, [])

    logging.info(
        f"Fetched {len(flattened_recent_tweets)} tweets from twitter for {SEARCH_TERMS} terms"
    )

    return [json.dumps(tweet) for tweet in map(dictify_tweet, flattened_recent_tweets)]
