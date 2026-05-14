from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE SETUP ---
Base = declarative_base()

# Uses the absolute path from your .env: E:/AuthenticationFYP-main/Authentication/auth.db
engine = create_engine(os.getenv("DB_URL"), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- DATABASE MODELS ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    hash_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# Create the tables in the fresh auth.db if they don't exist
Base.metadata.create_all(bind=engine)

# --- PYDANTIC SCHEMAS (For FastAPI) ---
class UserCreate(BaseModel):
    username: str
    email: str
    role: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None