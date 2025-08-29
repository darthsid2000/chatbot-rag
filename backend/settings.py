import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INDEX_DIR = os.getenv("INDEX_DIR", "index")
XML_PATH = os.getenv("XML_PATH", "stormlightarchive_pages_current.xml")
TOP_K = int(os.getenv("TOP_K", "4"))