from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

# Explicitly use Psycopg 2
database_url = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg2://",
    1
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

def test_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
