"""Base Module to sync with individual stores (IRs)"""
import os
import datetime
from redis_om import get_redis_connection, EmbeddedJsonModel, JsonModel, Field, Migrator
from dotenv import load_dotenv


load_dotenv()

redis = get_redis_connection(
    host=os.getenv('HOST'),
    port=os.getenv('PORT'),
    password=os.getenv('PASSWORD'),
    decode_responses=True,
)


class Author(EmbeddedJsonModel):
    first_name: str = Field(index=True, full_text_search=True)
    last_name: str
    email: str
    bio: str
    date_joined: datetime.date = Field(default=datetime.datetime.now())

    class Meta:
        database = redis


class Blog(JsonModel):
    title: str = Field(index=True, full_text_search=True)
    content: str
    author: Author
    date_posted: datetime.date = Field(
        default=datetime.datetime.today().strftime("%Y-%m-%d")
    )

    class Meta:
        database = redis


Migrator().run()

req = {
  "title": "Sample Blog Title",
  "content": "This is the content of the blog post. Lorem ipsum...",
  "author": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "bio": "A passionate writer and blogger.",
    "date_joined": "2022-01-01"
  },
}

k = Blog(**req)
k.save()
