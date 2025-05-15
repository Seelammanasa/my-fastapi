from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://manasa:manasa@13.49.241.233/eat_pizza"
engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,bind=engine)