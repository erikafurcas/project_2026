from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from sqlmodel import SQLModel, Field

# Modello RIGIDO per l'input delle API
class EventCreate(BaseModel):
    model_config = ConfigDict(strict=True)  # Forza il lancio del 422 in caso di tipi errati
    
    title: StrictStr
    description: StrictStr
    date: datetime  # Pydantic respingerà autonomamente stringhe invalide come "not-a-date"
    location: StrictStr

# Modello per la Tabella del Database
class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    date: datetime
    location: str
