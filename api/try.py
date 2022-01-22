# import psycopg2
# from psycopg2 import Error

# try:
#     # Connect to an existing database
#     connection = psycopg2.connect(user="raj",
#                                   password="1234",
#                                   host="127.0.0.1",
#                                   port="5432",
#                                   database="postgres")

#     # Create a cursor to perform database operations
#     cursor = connection.cursor()
#     # Print PostgreSQL details
#     print("PostgreSQL server information")
#     print(connection.get_dsn_parameters(), "\n")
#     # Executing a SQL query
#     cursor.execute("SELECT * from posts")
#     # Fetch result
#     record = cursor.fetchone()
#     print("You are connected to - ", record, "\n")

# except (Exception, Error) as error:
#     print("Error while connecting to PostgreSQL", error)
# finally:
#     if (connection):
#         cursor.close()
#         connection.close()
#         print("PostgreSQL connection is closed")

# sql testing starts from here
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import TIMESTAMP 
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

# SQLALCHEMY_DATABASE_URL = "postgresql://raj:1234@localhost:5432/postgres"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# for postgresql
# engine = create_engine('postgresql+psycopg2://raj:1234@localhost/postgres')
engine = create_engine("mysql://root:root@localhost/gymapi", echo = True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String(200),nullable=False)
    content = Column(String(200),nullable=False)
    published = Column(Boolean,default=True,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,default='now()')

    # def __repr__(self):
    #     return f"User(id={self.id !r}, title={self.title !r}, content={self.content !r}, published={self.published !r}, created={self.created !r})"
Base.metadata.create_all(engine)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
