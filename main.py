from fastapi import FastAPI, HTTPException
from models import *
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

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
