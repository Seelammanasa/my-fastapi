from fastapi import FastAPI,Depends, Form,HTTPException, Query,status
from db import SessionLocal,engine
from schemas import GetSalaryTipsResponseModel, SalaryTipsListModel, SalaryTipsResultModel, User,UserCreate,UserOut,Token
from models import User,Base, UserDetails
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta
import models,schemas,curd
from sqlalchemy.orm import Session
import uuid

app=FastAPI()

Base.metadata.create_all(bind=engine)

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY="eat_pizza_sure"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context=CryptContext(schemes=["bcrypt"])

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
def create_access_token(data: dict, expires_delta=timedelta):
    to_encode=data.copy()
    expire=datetime.utcnow()+expires_delta
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt
def create_refresh_token(data: dict, expires_delta=timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt    

def generate_encrypted_key():
    return str(uuid.uuid4())
def generate_user_id():
    return str(uuid.uuid4())
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
def authenticate_user(db:Session, email:str,password:str):
    print(email)
    print(password)
    user=curd.get_user_by_email(db,email=email)
    print(user)
    if not user or not verify_password(password,user.hashed_password):
        return False
    print(user)
    return user
@app.post("/register_user")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    db_user = curd.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=404,detail={"status": "success", "message": "Email already registered"})
    hashed_password = pwd_context.hash(password)
    user_data = schemas.UserCreate(
        username=username, email=email, password=hashed_password
    )
    created_user = curd.create_user(db=db, user=user_data)
    access_token_expries=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(data={"sub": created_user.email}, expires_delta= access_token_expries)
    refresh_token_expries=timedelta(days=10)
    refresh_token=create_refresh_token(data={"sub": created_user.email}, expires_delta=refresh_token_expries)
    encrypted_key=generate_encrypted_key()
    
    return {
        "status": "success",
        "message": "Successfully Registered.",
        "result": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "encryptedKey": encrypted_key,
        },
    }

@app.post("/login_user")
async def login_for_access_token(data: schemas.LoginRequest,db:Session=Depends(get_db)):
    user=authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expire=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(data={"sub":user.email},expires_delta=access_token_expire)
    refresh_token_expries=timedelta(days=10)
    refresh_token=create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expries)
    """user_id=generate_user_id()
    encrypted_key=generate_encrypted_key()
    curd.create_user_details(db, user_id, user.id)"""
    user_details = db.query(UserDetails).filter(UserDetails.user_register_id == user.id).first()
    encrypted_key = generate_encrypted_key()

    if user_details:
        user_id = user_details.user_id  
    else:
        user_id = generate_user_id()  
        curd.create_user_details(db, user_id, user.id)

    return {
        "status":"success",
        "message":"Successfully Login",
        "user_id":user_id,
        "result":{
            "access_token":access_token,
            "refresh_token":refresh_token,
            "encryptedKey": encrypted_key,

        },
    }
@app.get("/get_user_details/{user_id}")
async def get_user_details(
    user_id: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not curd.validate_user_id(user_id):
        print(f"User ID validation failed for: {user_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")
    user_session = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    if not user_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User session not found")
    user = db.query(User).filter(User.id == user_session.user_register_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
         "details": "User details fetched successfully",
        "user_id": user_id,
        "email": user.email,
        "username": user.username
       
    }
@app.get("/get_salary_tips/{user_id}", response_model=GetSalaryTipsResponseModel)
async def get_salary_tips(
    user_id: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not db.query(UserDetails).filter(UserDetails.user_id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    salary_tips_list = [
        SalaryTipsResultModel(salaryTipsId="1", tips="Always ask for the top of your salary range."),
        SalaryTipsResultModel(salaryTipsId="2", tips="Research market salary before negotiation."),
        SalaryTipsResultModel(salaryTipsId="3", tips="Be confident but not aggressive."),
        SalaryTipsResultModel(salaryTipsId="4", tips="Highlight your skills and achievements."),
        SalaryTipsResultModel(salaryTipsId="5", tips="Don't reveal your previous salary."),
        SalaryTipsResultModel(salaryTipsId="6", tips="Negotiate more than just salary (benefits, bonuses)."),
        SalaryTipsResultModel(salaryTipsId="7", tips="Practice negotiation conversations beforehand."),
        SalaryTipsResultModel(salaryTipsId="8", tips="Don't accept the first offer immediately."),
        SalaryTipsResultModel(salaryTipsId="9", tips="Ask for time to consider the offer."),
        SalaryTipsResultModel(salaryTipsId="10", tips="Be willing to walk away if the offer isn't fair.")
    ]

    return {
        "status": "success",
        "message": "Salary tips fetched successfully",
        "result": SalaryTipsListModel(
            totalCount=len(salary_tips_list),
            list=salary_tips_list
        )
    }