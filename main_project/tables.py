from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel



class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str
    winstreak: int = 0


