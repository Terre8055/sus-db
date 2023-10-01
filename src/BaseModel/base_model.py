"""Base Module to sync with individual stores (IRs)"""
from typing import Optional
from redis_om import HashModel
from pydantic import EmailStr
from dotenv import load_dotenv
from user_store import user_db_manager

load_dotenv()


class BaseModel(HashModel, user_db_manager.UserDBManager):
    """Base Model ----Central Station"""
    name: str
    age: int
    email: EmailStr
    about: Optional[str]




