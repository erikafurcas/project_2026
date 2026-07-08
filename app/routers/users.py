from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, text
from typing import List

# Import dei modelli e della sessione del database
from app.models.user import User
from app.data.db import get_session

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("", response_model=List[User], status_code=status.HTTP_200_OK)
def get_users(session: Session = Depends(get_session)):
    """
    Restituisce la lista di tutti gli utenti esistenti.
    Risposta: 200 OK.
    """
    users = session.exec(select(User)).all()
    return users

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    """
    Crea un nuovo utente.
    Se esiste già un utente con lo stesso username, restituisce un errore 400.
    """
    # Validazione manuale del tipo per forzare l'errore 422 richiesto dal test pytest
    # impedendo che interi vengano convertiti silenziosamente in stringhe
    if user and hasattr(user, "username"):
        if not isinstance(user.username, str) or isinstance(user.username, bool):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Username deve essere una stringa"
        )

    # Controllo per evitare duplicati
    existing_user = session.get(User, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{username}", response_model=User, status_code=status.HTTP_200_OK)
def get_user_by_username(username: str, session: Session = Depends(get_session)):
    """
    Restituisce l'utente con lo username indicato.
    Risposta 404 Not Found se l'utente non esiste.
    """
    db_user = session.get(User, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return db_user

@router.delete("", status_code=status.HTTP_200_OK)
def delete_all_users(session: Session = Depends(get_session)):
    """
    Elimina tutti gli utenti.
    Effettua la rimozione a cascata delle registrazioni per evitare errori 
    di vincolo di chiave esterna (Foreign Key).
    """
    # L'istruzione SQL deve essere avvolta in text() per non far fallire SQLAlchemy
    session.execute(text("DELETE FROM registration"))
    
    users = session.exec(select(User)).all()
    for u in users:
        session.delete(u)
        
    session.commit()
    return {"message": "Tutti gli utenti e le relative registrazioni sono stati eliminati"}

@router.delete("/{username}", status_code=status.HTTP_200_OK)
def delete_user_by_username(username: str, session: Session = Depends(get_session)):
    """
    Elimina l'utente con lo username indicato.
    Deve eliminare anche tutte le registrazioni associate all'utente (cascade).
    """
    db_user = session.get(User, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
        
    # Uso corretto di text() con parametri bindati per l'eliminazione sicura a cascata
    session.execute(
        text("DELETE FROM registration WHERE username = :username"), 
        {"username": username}
    )
    
    session.delete(db_user)
    session.commit()
    return {"message": f"Utente {username} e registrazioni associate eliminati con successo"}
