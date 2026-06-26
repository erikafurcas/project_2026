from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.data.db import get_session
from app.models.user import User
from app.models.registration import Registration

#inizializzazione
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    """Restituisce la lista di tutti gli utenti."""
    return session.exec(select(User)).all()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    """Crea un nuovo utente. Ritorna errore 400 se lo username esiste già."""
    existing_user = session.get(User, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username già esistente")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{username}", response_model=User)
def get_user(username: str, session: Session = Depends(get_session)):
    """Restituisce l'utente cercato."""
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return user


# API Opzionali
@router.delete("/", status_code=status.HTTP_200_OK)
def delete_all_users(session: Session = Depends(get_session)):
    """Elimina tutti gli utenti e svuota le registrazioni per evitare errori di vincolo."""
    # Svuotiamo prima le registrazioni
    registrations = session.exec(select(Registration)).all()
    for reg in registrations:
        session.delete(reg)
        
    # Eliminiamo gli utenti
    users = session.exec(select(User)).all()
    for u in users:
        session.delete(u)
    session.commit()
    return {"Tutti gli utenti e le registrazioni associate sono stati eliminati"}

@router.delete("/{username}", status_code=status.HTTP_200_OK)
def delete_user(username: str, session: Session = Depends(get_session)):
    """Elimina l'utente indicato ed effettua il cascade sulle registrazioni."""
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    # Cascade manuale sulle registrazioni collegate a questo specifico utente
    registrations = session.exec(select(Registration).where(Registration.username == username)).all()
    for reg in registrations:
        session.delete(reg)

    session.delete(user)
    session.commit()
    return {f"Utente {username} eliminato con successo"}
