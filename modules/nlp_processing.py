import spacy
from dateparser import parse

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    """
    Extract key entities: DATE, PERSON, ORG, GPE
    """
    doc = nlp(text)
    entities = {"DATE": [], "PERSON": [], "ORG": [], "GPE": []}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    return entities


def normalize_date(date_str):
    """
    Convert date string to YYYY-MM-DD format
    """
    dt = parse(date_str)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return None
