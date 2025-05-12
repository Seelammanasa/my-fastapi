from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey,String,Integer

Base = declarative_base()

class User(Base):
    __tablename__="user_register"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(150),index=True)
    email=Column(String(150),unique=True,index=True)
    hashed_password=Column(String(150))
class UserDetails(Base):
    __tablename__="user_details"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(150), unique=True, index=True)  
    user_register_id = Column(Integer, ForeignKey('user_register.id'))  