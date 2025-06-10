from fastapi import FastAPI, HTTPException, Depends, Header, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import *

# Конфигурация секретного ключа для подписи токенов
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48

app = FastAPI()

DB: List[Advertisement] = []

@app.post("/advertisement", response_model=Advertisement)
def create_ad(ad: Advertisement):
    DB.append(ad)
    return ad

@app.get("/advertisement/{advertisement_id}", response_model=Advertisement)
def get_ad(advertisement_id: int):
    for ad in DB:
        if ad.id == advertisement_id:
            return ad
    raise HTTPException(status_code=404, detail="Advertisement not found")

@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement)
def update_ad(advertisement_id: int, ad_update: AdvertisementUpdate):
    for i, ad in enumerate(DB):
        if ad.id == advertisement_id:
            updated_data = ad.dict()
            update_fields = ad_update.dict(exclude_unset=True)
            updated_data.update(update_fields)
            updated_ad = Advertisement(**updated_data)
            DB[i] = updated_ad
            return updated_ad
    raise HTTPException(status_code=404, detail="Advertisement not found")

@app.delete("/advertisement/{advertisement_id}")
def delete_ad(advertisement_id: int):
    for i, ad in enumerate(DB):
        if ad.id == advertisement_id:
            DB.pop(i)
            return {"detail": "Advertisement deleted"}
    raise HTTPException(status_code=404, detail="Advertisement not found")

@app.get("/advertisement", response_model=List[Advertisement])
def search_ads(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    author_name: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
):
    results = DB
    if title:
        results = [ad for ad in results if title.lower() in ad.title.lower()]
    if description:
        results = [ad for ad in results if description.lower() in (ad.description or "").lower()]
    if price_min is not None:
        results = [ad for ad in results if ad.price >= price_min]
    if price_max is not None:
        results = [ad for ad in results if ad.price <= price_max]
    if author_name:
        results = [ad for ad in results if author_name.lower() in ad.author.name.lower()]
    if date_from:
        results = [ad for ad in results if ad.created_at >= date_from]
    if date_to:
        results = [ad for ad in results if ad.created_at <= date_to]
    return results

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=48))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Header(None)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("user_id"))
        user = next((u for u in users_db if u.id == user_id), None)
        return user
    except JWTError:
        return None

def has_permission(current_user: Optional[User], owner_id: Optional[int] = None, required_group: str = None):
    if current_user is None:
        # Неавторизованный пользователь
        if required_group is None:
            return True
        return False
    if current_user.group == "admin":
        return True
    if required_group is None:
        return True
    if current_user.id == owner_id:
        return True
    return False

# Роут для логина
@app.post("/login", response_model=Token)
def login(data: LoginData):
    user = next((u for u in users_db if u.username == data.username and u.password == data.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# CRUD для пользователей
@app.post("/user", response_model=User)
def create_user(user: UserCreate):
    if any(u.username == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = len(users_db) + 1
    new_user = User(id=user_id, username=user.username, password=user.password, group=user.group)
    users_db.append(new_user)
    return new_user

@app.get("/user/{user_id}")
def get_user(user_id: int, token: Optional[str] = Header(None)):
    current_user = get_current_user(token)
    user = next((u for u in users_db if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # права
    if current_user is None or (current_user.id != user_id and current_user.group != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

@app.patch("/user/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, token: Optional[str] = Header(None)):
    current_user = get_current_user(token)
    user = next((u for u in users_db if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # права
    if current_user is None or (current_user.id != user_id and current_user.group != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    if user_update.username:
        user.username = user_update.username
    if user_update.password:
        user.password = user_update.password
    if user_update.group and current_user.group == "admin":
        user.group = user_update.group
    return user

@app.delete("/user/{user_id}")
def delete_user(user_id: int, token: Optional[str] = Header(None)):
    current_user = get_current_user(token)
    user = next((u for u in users_db if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user is None or (current_user.id != user_id and current_user.group != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    users_db.remove(user)
    return {"detail": "User deleted"}
