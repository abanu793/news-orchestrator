import streamlit as st
from datetime import datetime
from modules import config
from modules.fetch_news import fetch_news
from modules.summarizer import generate_timeline
from modules.nlp_processing import extract_entities
import plotly.express as px
import pandas as pd
from langdetect import detect
import re

# ----------------------------
# Streamlit page setup
# ----------------------------
st.set_page_config(page_title="AI News Orchestrator", layout="wide")
st.title("📰 AI News Orchestrator")

# ----------------------------
# Robust SpaCy model loader
# ----------------------------
@st.cache_resource
def load_spacy_model():
    try:
        import spacy  # Import inside function to avoid cache issues
        return spacy.load("en_core_web_sm")
    except ImportError:
        st.error("❌ spaCy is not installed. Run `pip install spacy`.")
        raise
    except OSError:
        st.info("Downloading spaCy model 'en_core_web_sm' ...")
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        import spacy
        return spacy.load("en_core_web_sm")

# Load spaCy model safely
nlp = load_spacy_model()

# ----------------------------
# Cache news fetching to avoid repeated API calls
# ----------------------------
@st.cache_data(ttl=600)
def fetch_news_cached(topic):
    return fetch_news(topic)

# ----------------------------
# Cache timeline generation to reduce processing time
# ----------------------------
@st.cache_data(ttl=600)
def generate_timeline_cached(articles, api_key, topic):
    return generate_timeline(articles, api_key, topic=topic)

# ----------------------------
# User input
# ----------------------------
topic = st.text_input("Enter an event/topic")

if topic:
    st.info("🔍 Fetching news...")
    articles = fetch_news_cached(topic)

    if not articles:
        st.error("❌ No articles found for this topic.")
    else:
        st.success(f"Found {len(articles)} articles.")

        # ----------------------------
        # Detect article languages
        # ----------------------------
        for article in articles:
            content = article.get("content") or article.get("title") or ""
            try:
                article["language"] = detect(content)
            except:
                article["language"] = "unknown"

        # ----------------------------
        # Basic Bias / Authenticity Score
        # ----------------------------
        for article in articles:
            title = article.get("title", "").lower()
            if any(
                word in title for word in ["breaking", "shocking", "you won't believe"]
            ):
                article["source_score"] = 2
            else:
                article["source_score"] = 4  # default medium-high reliability

        # ----------------------------
        # Generate AI summary
        # ----------------------------
        timeline_output = generate_timeline_cached(
            articles, config.OPENAI_API_KEY, topic
        )

        # ----------------------------
        # Fact consistency check
        # ----------------------------
        statements = {}
        for article in articles:
            content = article.get("content") or ""
            nums_dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b|\b\d+\b", content)
            for nd in nums_dates:
                statements.setdefault(nd, []).append(article["title"])
        conflicts = {k: v for k, v in statements.items() if len(v) > 1}

        # ----------------------------
        # Display summary
        # ----------------------------
        st.header("📝 Summary")
        st.write(timeline_output.get("summary", "No summary available."))

        # ----------------------------
        # Extract and display entities
        # ----------------------------
        entities = extract_entities(timeline_output.get("summary", ""))
        if any(entities.values()):
            st.subheader("🔹 Key Entities")
            for ent_type, items in entities.items():
                if items:
                    st.markdown(f"**{ent_type}:** {', '.join(set(items))}")

        # ----------------------------
        # Display timeline & article cards
        # ----------------------------
        st.header("🗓 Timeline & Sources")
        for item in timeline_output.get("timeline", []):
            pub_date = item.get("publishedAt", "")
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except:
                pass

            title = item.get("title", "No title")
            url = item.get("url", "#")
            description = item.get("content", "")
            image_url = item.get("urlToImage", None)
            source_score = item.get("source_score", 3)
            language = item.get("language", "unknown")
            conflict_flag = "⚠️" if title in sum(conflicts.values(), []) else ""

            st.markdown("---")
            cols = st.columns([1, 3])
            with cols[0]:
                if image_url:
                    st.image(image_url, width=120)
            with cols[1]:
                st.markdown(f"**{pub_date}** → [{title}]({url}) {conflict_flag}")
                st.write(description[:200] + "..." if description else "")
                st.markdown(
                    f"**Source reliability:** {'⭐'*source_score} ({source_score}/5) | Language: {language}"
                )

        st.markdown("---")
        st.info("✅ All articles loaded.")

        # ----------------------------
        # Enhanced interactive timeline chart
        # ----------------------------
        timeline_data = []
        for item in timeline_output.get("timeline", []):
            pub_date = item.get("publishedAt", "")
            try:
                pub_date_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                continue
            snippet = item.get("content", "")
            snippet = snippet[:100] + "..." if snippet else ""
            timeline_data.append(
                {
                    "Date": pub_date_dt,
                    "Title": item.get("title", "No title"),
                    "Source": item.get("url", "#"),
                    "Snippet": snippet,
                    "Reliability": item.get("source_score", 3),
                }
            )

        # Limit timeline to first 50 articles for performance
        timeline_data = timeline_data[:50]

        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            color_map = {5: "green", 4: "blue", 3: "orange", 2: "red"}
            df_timeline["Color"] = df_timeline["Reliability"].map(color_map)

            fig = px.timeline(
                df_timeline,
                x_start="Date",
                x_end="Date",
                y="Title",
                hover_data=["Source", "Snippet", "Reliability"],
                color="Color",
                title="📊 Event Timeline",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
