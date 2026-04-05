import csv
import io
import random
import string
from sqlalchemy.orm import Session
from app.models.domain import User, URL
from typing import List, Dict

def parse_users_csv(file_content: str) -> List[Dict[str, str]]:
    users = []
    reader = csv.DictReader(io.StringIO(file_content))
    for row in reader:
        if "username" in row and "email" in row and row["username"] and row["email"]:
            users.append({"username": row["username"], "email": row["email"]})
    return users

def generate_short_code(db: Session, length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        if not db.query(URL).filter(URL.short_code == short_code).first():
            return short_code
