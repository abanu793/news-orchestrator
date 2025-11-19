# --- Using spacy-lite (no heavy model required) ---
from spacy_legacy import Language
import re
from dateparser import parse

# Create a lightweight NLP pipeline
nlp = Language()


def extract_entities(text):
    """
    Extract simple entities: DATE, PERSON, ORG, GPE using rule-based matching
    (since spacy-lite does not include models).
    """

    entities = {"DATE": [], "PERSON": [], "ORG": [], "GPE": []}

    # --- DATE extraction (using dateparser) ---
    date_matches = re.findall(
        r"\b(?:\d{1,2}\s\w+\s\d{4}|\w+\s\d{1,2},\s\d{4}|\d{4})\b", text
    )
    for d in date_matches:
        normalized = normalize_date(d)
        if normalized:
            entities["DATE"].append(normalized)

    # --- PERSON/GPE/ORG (very basic heuristics) ---
    words = text.split()

    # Capitalized words → possible PERSON/GPE/ORG
    for w in words:
        if w.istitle() and len(w) > 2:
            # naive classification
            if w in ["India", "USA", "China", "London", "Paris"]:
                entities["GPE"].append(w)
            else:
                entities["PERSON"].append(w)

    # ORG keyword-based detection
    org_keywords = [
        "Inc",
        "Ltd",
        "Corporation",
        "Company",
        "Corp",
        "Tech",
        "Google",
        "Microsoft",
        "Amazon",
    ]
    for kw in org_keywords:
        if kw in text:
            entities["ORG"].append(kw)

    return entities


def normalize_date(date_str):
    """
    Convert date string to YYYY-MM-DD format
    """
    dt = parse(date_str)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return None
