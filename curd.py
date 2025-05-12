import re
from sqlalchemy.orm import Session
from models import User, UserDetails
from schemas import UserCreate
from db import SessionLocal

def get_user_by_email(db:Session, email:str):
    print(email)
    print(User.email)
    return db.query(User).filter(User.email == email).first()
def create_user(db:Session,user:UserCreate):
    db_user=User(username=user.username,email=user.email,hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def validate_user_id(user_id: str) -> bool:
    uuid_regex = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    print(f"Validating user_id: {user_id}")
    return re.match(uuid_regex, user_id) is not None
def create_user_details(db: Session, user_id: str, user_register_id: int):
    db_session = UserDetails(user_id=user_id, user_register_id=user_register_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session