from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import Event
from app.models.schemas import EventOut
from typing import List
from app.cache import get_redis_client, get_cache, set_cache

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_model=List[EventOut])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    redis_client = get_redis_client()
    cache_key = f"events:skip={skip}:limit={limit}"
    
    cached = get_cache(redis_client, cache_key)
    if cached is not None:
        return cached

    events = db.query(Event).order_by(Event.id).offset(skip).limit(limit).all()
    events_out = [EventOut.model_validate(e) for e in events]
    set_cache(redis_client, cache_key, events_out, ttl=15)
    return events_out
