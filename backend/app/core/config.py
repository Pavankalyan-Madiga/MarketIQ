
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://marketing_user:marketing_pass_2026@localhost:5433/marketing_intelligence"
)
