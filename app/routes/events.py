from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import Event
from app.models.schemas import EventOut
from typing import List

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_model=List[EventOut])
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()
