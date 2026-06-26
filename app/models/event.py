from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Event(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True) # ID assegnato automaticamente
    title: str
    description: str
    date: datetime # Usiamo il tipo datetime di Python
    location: str