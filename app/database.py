import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.environ.get('DATABASE_USER', 'postgres')}:{os.environ.get('DATABASE_PASSWORD', 'postgres')}@{os.environ.get('DATABASE_HOST', 'localhost')}:{os.environ.get('DATABASE_PORT', '5432')}/{os.environ.get('DATABASE_NAME', 'hackathon_db')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
