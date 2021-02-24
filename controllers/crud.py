from sqlalchemy.orm import Session
# Import model and schemas from other folders
from core.models import users
from core.schemas import user_schemas
# Import JWT and authentication dependencies needed
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
# Allowing you to use different hashing algorithms
from passlib.context import CryptContext
# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from typing import Optional

load_dotenv()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

# Hash password coming from user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Utility to verify if a received password matches the hash stored
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

# Retrieve a user based on their email
def get_user(db, email: str):
    return db.query(users.User).filter(users.User.email==email)

def create_user(db: Session, user: user_schemas.UserCreate):
    db_user = users.User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate and return a user
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def get_user(db: Session, user_id: int):
#     return db.query(users.User).filter(users.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(users.User).filter(users.User.email == email).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(users.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: user_schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = users.User(
#         first_name=user.first_name,
#         last_name=user.last_name,
#         phone=user.phone,
#         email=user.email, 
#         password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
