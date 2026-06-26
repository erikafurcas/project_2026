from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True) # Questa è la chiave primaria, avere un indice migliora leggermente le prestazioni di lettura nel database
    name: str
    email: str
