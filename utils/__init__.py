### A Utils module to contain utility methods

import os

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


def dictify_tweet(tweet):
    return (
        {
            "data": tweet.data if tweet.data else None,
            "id": tweet.id if tweet.id else None,
            "text": tweet.text if tweet.text else None,
            "attachments": tweet.attachments if tweet.attachments else None,
            "author_id": tweet.author_id if tweet.author_id else None,
            "context_annotations": tweet.context_annotations
            if tweet.context_annotations
            else None,
            "conversation_id": tweet.conversation_id if tweet.conversation_id else None,
            "created_at": tweet.created_at if tweet.created_at else None,
            "entities": tweet.entities if tweet.entities else None,
            "geo": tweet.geo if tweet.geo else None,
            "in_reply_to_user_id": tweet.in_reply_to_user_id
            if tweet.in_reply_to_user_id
            else None,
            "lang": tweet.lang if tweet.lang else None,
            "non_public_metrics": tweet.non_public_metrics
            if tweet.non_public_metrics
            else None,
            "organic_metrics": tweet.organic_metrics if tweet.organic_metrics else None,
            "possibly_sensitive": tweet.possibly_sensitive
            if tweet.possibly_sensitive
            else None,
            "promoted_metrics": tweet.promoted_metrics
            if tweet.promoted_metrics
            else None,
            "public_metrics": tweet.public_metrics if tweet.public_metrics else None,
            "referenced_tweets": tweet.referenced_tweets
            if tweet.referenced_tweets
            else None,
            "reply_settings": tweet.reply_settings if tweet.reply_settings else None,
            "source": tweet.source if tweet.source else None,
            "withheld": tweet.withheld if tweet.withheld else None,
        }
        if tweet
        else {}
    )


def add_text_analysis_to_tweet(tweet_dict, response):
    tweet_dict["id"] = str(tweet_dict["id"])  # cosmosDB doesn't like int id
    tweet_dict["sentiment"] = response.sentiment
    tweet_dict["confidence_scores"] = {
        "positive": response.confidence_scores["positive"],
        "neutral": response.confidence_scores["neutral"],
        "negative": response.confidence_scores["negative"],
    }


key = os.getenv("AZURE_AI_CREDENTIAL_KEY")
endpoint = os.getenv("AZURE_AI_CREDENTIAL_ENDPOINT")


# Authenticate the client using your key and endpoint
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential
    )
    return text_analytics_client
