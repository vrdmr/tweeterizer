import functools
import json
import logging
import operator
import os
from typing import List

import azure.functions as func
import tweepy

from utils import (add_text_analysis_to_tweet, authenticate_client,
                   dictify_tweet)

app = func.FunctionApp()


FETCH_TWEETS_COUNT = 30
"""Fetch these many number of tweets"""
SEARCH_TERMS = ["PyCon", "Python", "Azure"]

TWITTER_CLIENT = tweepy.Client(os.environ.get("BEARER_TOKEN"))
AZURE_AI_CLIENT = authenticate_client()

@app.function_name("FetchTweets")
@app.schedule(schedule="0 0 * * * *", arg_name="timer", run_on_startup=True)
@app.write_event_hub_message(
    arg_name="$return", event_hub_name="tweets_queue", connection="TWEETS_EH_CONNECTION"
)
def main(timer: func.TimerRequest) -> str:
    recent_tweets = [
        TWITTER_CLIENT.search_recent_tweets(term, max_results=FETCH_TWEETS_COUNT).data
        for term in SEARCH_TERMS
    ]

    flattened_recent_tweets = functools.reduce(operator.iconcat, recent_tweets, [])

    logging.info(
        f"Fetched {len(flattened_recent_tweets)} tweets from twitter for {SEARCH_TERMS} terms"
    )

    return [json.dumps(tweet) for tweet in map(dictify_tweet, flattened_recent_tweets)]


@app.function_name(name="AnalyzeLoadTweets")
@app.on_event_hub_message(
    arg_name="events",
    event_hub_name="tweets_queue",
    connection="TWEETS_EH_CONNECTION",
    cardinality="many",
    consumer_group="$Default",
)
@app.write_cosmos_db_documents(
    arg_name="tweetdoc",
    database_name="tweetsdatabase",
    collection_name="tweetscollection",
    connection_string_setting="tweetspycon_DOCUMENTDB",
)
def send_to_cosmos_db(
    events: List[func.EventHubEvent], tweetdoc: func.Out[func.Document]
):
    logging.info(f"Got {len(events)} events from EventHub")

    tweets_json = []
    for event in events:
        tweet_dict = json.loads(event.get_body().decode("utf-8"))
        response = AZURE_AI_CLIENT.analyze_sentiment(
            documents=[tweet_dict["text"]], show_opinion_mining=True
        )[0]
        add_text_analysis_to_tweet(tweet_dict=tweet_dict, response=response)
        tweets_json.append(tweet_dict)

    logging.info(f"{len(tweets_json)} records being sent to CosmosDB")
    for tweet in tweets_json:
        tweetdoc.set(func.Document.from_json(json.dumps(tweet)))
