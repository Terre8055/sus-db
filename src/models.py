"""Base Module to sync with individual stores (IRs)"""
import datetime
from typing import Optional
from redis_om import EmbeddedJsonModel, JsonModel, Field, Migrator
from pydantic import FilePath
from user_store.user_db_manager import UserDBManager
from settings import redis


print(redis)

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


class Account(JsonModel):
    """Account model to be associated with transactions"""
    account_name : str = Field(index=True, full_text_search=True, max_length=64)
    organization_number : str
    priority : Optional[str]
    annual_revenue : Optional[str]
    phone : Optional[str]
    address : Address
    category : str
    is_owner: bool = Field(default=False)
    website : Optional[str]
    description : str
    created_on : datetime.date = Field(default=datetime.datetime.now())
    is_active : bool = Field(default=True)
    tags : Optional[str]
    status : str


    class Meta:
        """Define additional configuraion"""
        database = redis


    def __str__(self):
        """Representation of account model"""
        return f"{self.account_name}"


class Billing(EmbeddedJsonModel):
    """Customer Billing Info Model"""
    billing_address_line : str
    billing_street : str
    billing_city : str
    billing_state : str
    billing_postcode : str
    billing_country : str

    class Meta:
        """Define additional configuraion"""
        database = redis

    def __str__(self):
        """Method to retrive complete address from model"""
        billing_address = ""
        if self.billing_address_line:
            billing_address += self.billing_address_line
        if self.billing_street:
            if billing_address:
                billing_address += ", " + self.billing_street
            else:
                billing_address += self.billing_street
        if self.billing_city:
            if billing_address:
                billing_address += ", " + self.billing_city
            else:
                billing_address += self.billing_city
        if self.billing_state:
            if billing_address:
                billing_address += ", " + self.billing_state
            else:
                billing_address += self.billing_state
        if self.billing_country:
            if billing_address:
                billing_address += self.billing_country
        return billing_address


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
    billing: Billing

    class Meta:
        """Define additional configuraion"""
        database = redis

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



Migrator().run()


