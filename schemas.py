from pydantic import BaseModel
from typing import List 


class UserBase(BaseModel):
    username:str
    email:str
class UserCreate(UserBase):
    password:str
class User(UserBase):
    id:int
    class Config:
        orm_mode=True
class Token(BaseModel):
    access_token:str
    token_type:str
class UserOut(BaseModel):
    id:int
    username:str
    email:str
    class Config:
        orm_mode=True
class SalaryTipsResultModel(BaseModel):
    salaryTipsId: str
    tips: str

class SalaryTipsListModel(BaseModel):
    totalCount: int
    list: List[SalaryTipsResultModel]

class GetSalaryTipsResponseModel(BaseModel):
    status: str
    message: str
    result: SalaryTipsListModel
