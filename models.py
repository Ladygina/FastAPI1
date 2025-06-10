from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import datetime
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    password: str
    group: str  # 'user' или 'admin'

    def to_dict(self):
        return {'id': self.id, "name": self.username}

# Временно хранилище пользователей
users_db: List[User] = []

# Модель для логина
class LoginData(BaseModel):
    username: str
    password: str

# Модель токена
class Token(BaseModel):
    access_token: str
    token_type: str

# Модели для пользователей API
class UserCreate(BaseModel):
    username: str
    password: str
    group: str = "user"  # по умолчанию 'user'

class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]
    group: Optional[str]


# class Author(BaseModel):
#     id: int
#     name: str
#
#     def to_dict(self):
#         return {'id': self.id, "name": self.name}


class Advertisement(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: User
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[User] = None


# "БД" в памяти