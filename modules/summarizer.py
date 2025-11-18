import openai
import re


def generate_timeline(articles, api_key, topic=""):
    """
    Generate AI summary from a list of articles.
    If AI fails (quota/API error), returns a dummy topic-based summary.
    Timeline always uses real articles.
    """
    openai.api_key = api_key

    if not articles:
        return {"summary": "No articles available.", "timeline": []}

    # Sort articles by published date
    articles_sorted = sorted(articles, key=lambda x: x.get("publishedAt", ""))

    # Build AI prompt
    prompt = "You are an AI assistant. Generate:\n"
    prompt += "1. A concise summary of the event/topic based on these articles.\n"
    prompt += (
        "2. A chronological timeline in the format YYYY-MM-DD → Event description.\n\n"
    )
    prompt += "Articles:\n"
    for a in articles_sorted:
        content = a.get("content") or ""
        title = a.get("title") or ""
        prompt += f"{a.get('publishedAt','')} - {title}: {content}\n"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
        )
        text = response.choices[0].message.content

        # Extract summary & timeline
        summary_match = re.search(
            r"(Summary[:\s]*)(.*?)(Timeline[:\s]*)(.*)", text, re.DOTALL | re.IGNORECASE
        )
        if summary_match:
            summary = summary_match.group(2).strip()
        else:
            summary = text

        return {"summary": summary, "timeline": articles_sorted}

    except Exception:
        # --- Fallback: AI unavailable ---
        dummy_summary = (
            f"The topic '{topic}' has been widely discussed recently. "
            "Several news outlets reported on key developments, milestones, and announcements."
        )

        # Timeline always uses actual articles
        return {"summary": dummy_summary, "timeline": articles_sorted}
