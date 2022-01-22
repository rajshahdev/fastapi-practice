from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from api.config import settings
# settings = config.settings

# SQLALCHEMY_DATABASE_URL = "postgresql://raj:1234@localhost:5432/postgres"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# for postgresql
engine = create_engine(f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}')

# engine = create_engine("mysql+pymysql://root:root@localhost/gymapi", paramstyle='format')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
