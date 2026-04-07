from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str
    winstreak: int = 0
    best_streak: int = 0  # maior sequência de vitórias

    battles: List["BattleHistory"] = Relationship(back_populates="user")

class BattleHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    opponent: str
    result: str  # "win" ou "loss"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="battles")