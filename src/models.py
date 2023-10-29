"""Base Module to sync with individual stores (IRs)"""
import datetime
from typing import Optional

from pydantic import FilePath
from redis_om import EmbeddedJsonModel, JsonModel, Field, Migrator

from src.settings import redis
from src.user_db_manager import UserDBManager


class User(JsonModel):
    """User Model"""
    username: Optional[str] = Field(default='admin000')
    title: Optional[str]
    email: Optional[str]
    bio: Optional[str]
    ir_id: str = Field(index=True)
    date_joined: str = Field(default=datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))

    class Meta:
        """Define additional configuration"""
        database = redis
        global_key_prefix = "sus-db"
        model_key_prefix = "user"

    def __str__(self) -> str:
        return f"{self.ir_id}"


class Session(JsonModel):
    session_id: Optional[str]
    is_authenticated: bool = Field(default=False)
    ir_id: str = Field(index=True)
    timestamp: str = Field(default=datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))

    class Meta:
        """Define additional configuration"""
        database = redis
        global_key_prefix = "sus-db"
        model_key_prefix = "session"
