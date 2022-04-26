import json
import logging
from typing import List

import azure.functions as func

from utils import add_text_analysis_to_tweet, authenticate_client

AZURE_AI_CLIENT = authenticate_client()


def main(events: List[func.EventHubEvent], tweetdoc: func.Out[func.Document]):
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
