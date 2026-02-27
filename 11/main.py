from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal

from textblob import TextBlob

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SentimentType = Literal["happy", "sad", "neutral"]


class SentencesRequest(BaseModel):
    sentences: List[str]


class SentimentResult(BaseModel):
    sentence: str
    sentiment: SentimentType


class SentimentResponse(BaseModel):
    results: List[SentimentResult]


def classify_sentiment(text: str) -> SentimentType:
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        return "happy"
    if polarity < -0.1:
        return "sad"
    return "neutral"


@app.post("/sentiment", response_model=SentimentResponse)
def get_sentiments(payload: SentencesRequest) -> SentimentResponse:
    results = [
        SentimentResult(sentence=s, sentiment=classify_sentiment(s))
        for s in payload.sentences
    ]
    return SentimentResponse(results=results)

