from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException,status
from passlib.context import CryptContext
from datetime import datetime,timedelta
from typing import Optional
from jose import JWTError, jwt
from Model import TokenData
from Model import get_db, User
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

password_context=CryptContext(schemes=["bcrypt"],deprecated='auto')
oauth2=OAuth2PasswordBearer(tokenUrl="token")

def get_password(password:str):
    return password_context.hash(password)

def verify_password(password:str,hash_password:str):
    return password_context.verify(password,hash_password)

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode=data.copy()
    if expires_delta:
        expires_delta=datetime.utcnow() + expires_delta
    else:
        expires_delta=datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp":expires_delta})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def verify_access_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str=payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token",headers={"WWW-Authenticate":"Bearer"})
        return TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token",headers={"WWW-Authenticate":"Bearer"})
    
def get_current_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    token_data=verify_access_token(token)
    user=db.query(User).filter(User.email==token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User does not exist",headers={"WWW-Authenticate":"Bearer"})
    return user

def get_current_active_user(current_user:User=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Inactive user")
    return current_user