from pydantic import BaseModel, ConfigDict, StrictStr, EmailStr
from sqlmodel import SQLModel, Field

# Modello RIGIDO per l'input delle API (Risolve il problema dei tipi errati/mancanti)
class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)  # Impedisce la conversione automatica da 0 a "0"
    
    username: StrictStr
    name: StrictStr
    email: EmailStr  # EmailStr valida automaticamente che sia un indirizzo email corretto

# Modello per la Tabella del Database
class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    name: str
    email: str
