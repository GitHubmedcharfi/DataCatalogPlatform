from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
DATABASE_URL = "postgresql://platform_user:FSShpc%402026@localhost:5432/platform_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
def create_tables():
    Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()