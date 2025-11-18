import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", 10))

if not NEWS_API_KEY:
    raise ValueError("❌ NEWS_API_KEY missing in .env")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing in .env")
