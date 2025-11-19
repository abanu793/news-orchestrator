from openai import OpenAI
from dateparser import parse
import os

client = OpenAI()


def extract_entities(text):
    """
    Extract entities using OpenAI (better than spaCy / spacy-lite)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract entities: DATE, PERSON, ORG, GPE. Return JSON only.",
            },
            {"role": "user", "content": text},
        ],
    )

    try:
        entities = eval(response.choices[0].message.content)
    except:
        entities = {"DATE": [], "PERSON": [], "ORG": [], "GPE": []}

    return entities


def normalize_date(date_str):
    dt = parse(date_str)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return None
