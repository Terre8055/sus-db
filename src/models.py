"""Base Module to sync with individual stores (IRs)"""
import datetime
from redis_om import EmbeddedJsonModel, JsonModel, Field, Migrator
from pydantic import FilePath
from user_store.user_db_manager import UserDBManager
from settings import redis


class Address(EmbeddedJsonModel):
    """Address Model"""
    address_line: str = Field(index=True, full_text_search=True)
    street: str
    city: str
    state: str
    country : str 

    class Meta:
        """Define additional configuraion"""
        database = redis

    def __str__(self):
        """Method to retrive complete address from model"""
        address = ""
        if self.address_line:
            address += self.address_line
        if self.street:
            if address:
                address += ", " + self.street
            else:
                address += self.street
        if self.city:
            if address:
                address += ", " + self.city
            else:
                address += self.city
        if self.state:
            if address:
                address += ", " + self.state
            else:
                address += self.state
        if self.country:
            if address:
                address += self.country
        return address


class User(JsonModel, UserDBManager):
    """User Model"""
    first_name: str = Field(index=True, full_text_search=True)
    last_name: str
    username:str = Field(default='admin000')
    title:str
    is_authenticated: bool = Field(default=False)
    is_authorized: bool = Field(default=False)
    profile_pic: FilePath
    email: str
    is_admin : bool = Field(default=True)
    phone : str = Field(default="+1(000)0000-000")
    website: str
    bio: str
    date_joined: datetime.date = Field(default=datetime.datetime.now())
    address: Address

    class Meta:
        """Define additional configuraion"""
        database = redis

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



Migrator().run()


