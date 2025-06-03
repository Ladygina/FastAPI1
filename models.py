from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import datetime
from typing import Optional, List
from datetime import datetime

class Author(BaseModel):
    id: int
    name: str

    def to_dict(self):
        return {'id': self.id, "name": self.name}

# Модель объявления
class Advertisement(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: Author
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Модель для обновления объявления
class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[Author] = None

# "БД" в памяти