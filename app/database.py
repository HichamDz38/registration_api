from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(
                                settings.POSTGRES_USER,
                                settings.POSTGRES_PASSWORD,
                                settings.POSTGRES_HOSTNAME,
                                settings.DATABASE_PORT,
                                settings.POSTGRES_DB
                            )
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
