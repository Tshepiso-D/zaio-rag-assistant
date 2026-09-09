import os
from dotenv import load_dotenv

load_dotenv()

# --- Paths -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDBOOK_PDF_PATH = os.path.join(BASE_DIR, "data", "handbook", "Student_Handbook.pdf")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
WEB_CACHE_DIR = os.path.join(BASE_DIR, "data", "web_cache")

# --- Website crawl -------------------------------------------------------
ZAIO_BASE_URL = "https://www.zaio.io"
ZAIO_ALLOWED_PATH_PREFIXES = ["/"]  # crawl within the zaio.io domain
ZAIO_MAX_PAGES = 40
ZAIO_SEED_PATHS = [
    "/",
    "/bootcamps",
    "/fullstack-ai-engineer-bootcamp",
    "/cloud-devops-engineer-bootcamp",
    "/fullstack-bootcamp",
    "/datascience-bootcamp",
    "/cybersecurity-bootcamp",
    "/digital-marketing-bootcamp",
    "/compare-courses",
    "/qualifications",
    "/qualifications/occupational-certificate-software-development",
    "/qualifications/occupational-certificate-cybersecurity",
    "/qualifications/occupational-certificate-data-science",
    "/aboutus",
    "/company",
    "/tuition-financing",
    "/refundPolicy",
    "/terms",
    "/community",
    "/learner-stories",
    "/events",
]

# --- Chunking ------------------------------------------------------------
CHUNK_SIZE = 800          # characters per chunk
CHUNK_OVERLAP = 150       # characters of overlap between consecutive chunks

# --- Embeddings ------------------------------------------------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"   # local, no API key required

# --- Retrieval -------------------------------------------------------------
TOP_K = 4
# Cosine-distance threshold (Chroma default space) above which we treat a
# result as "not relevant enough" -> triggers the fallback refusal message.
MAX_RELEVANT_DISTANCE = 0.75

# --- LLM generation ----------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GENERATION_MODEL = os.environ.get("GENERATION_MODEL", "claude-sonnet-4-6")

FALLBACK_MESSAGE = "I could not find that information in the available knowledge base."

COLLECTION_NAME = "zaio_knowledge_base"
