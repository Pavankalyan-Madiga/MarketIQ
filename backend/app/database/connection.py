
from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

def test_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True

