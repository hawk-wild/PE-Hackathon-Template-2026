from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class URLBase(BaseModel):
    original_url: str
    title: str

class URLCreate(URLBase):
    user_id: int

class URLUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class URLOut(URLBase):
    id: int
    user_id: int
    short_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    url_id: int
    user_id: int
    event_type: str
    details: Dict[str, Any]

class EventOut(EventBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
