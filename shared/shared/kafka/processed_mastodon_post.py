from typing import TypedDict, Literal

MIXED = "mixed"
NEUTRAL = "neutral"
POSITIVE = "positive"
NEGATIVE = "negative"

Sentiment = Literal["mixed", "neutral", "positive", "negative"]

class ProcessedMastodonPost(TypedDict):
    id: int
    sentiment: Sentiment
    analysis: str