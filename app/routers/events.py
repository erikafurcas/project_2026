from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.data.db import get_session
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration
from datetime import datetime

# Creiamo il router specifico per gli eventi
router_events = APIRouter(prefix="/events", tags=["events"])


@router_events.get("/", response_model=List[Event])
def get_events(session: Session = Depends(get_session)):
    """Restituisce la lista di tutti gli eventi esistenti."""
    return session.exec(select(Event)).all()


@router_events.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: Event, session: Session = Depends(get_session)):
    """Crea un nuovo evento."""
    if isinstance(event.date, str): #mi serve per convertire il formato data
        event.date = datetime.fromisoformat(event.date)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router_events.get("/{id}", response_model=Event)
def get_event(id: int, session: Session = Depends(get_session)):
    """Restituisce l'evento con l'id indicato."""
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


@router_events.put("/{id}", response_model=Event)
def update_event(id: int, updated_event: Event, session: Session = Depends(get_session)):
    """Aggiorna un evento esistente."""
    if isinstance(event.date, str):     #mi serve per convertire il formato data
        event.date = datetime.fromisoformat(event.date)
    db_event = session.get(Event, id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    data = updated_event.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key != "id":
            setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router_events.post("/{id}/register", status_code=status.HTTP_201_CREATED)
def register_to_event(id: int, user_data: User, session: Session = Depends(get_session)):
    """Registra un utente a un evento. Se l'utente non esiste, lo crea."""
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    user = session.get(User, user_data.username)
    if not user:
        user = User(username=user_data.username, name=user_data.name, email=user_data.email)
        session.add(user)
        session.commit()
        session.refresh(user)

    existing_reg = session.exec(
        select(Registration).where(Registration.username == user.username, Registration.event_id == id)
    ).first()

    if not existing_reg:
        registration = Registration(username=user.username, event_id=id)
        session.add(registration)
        session.commit()

    return {"message": "Registrazione effettuata con successo"}


# API Opzionali

@router_events.delete("/", status_code=status.HTTP_200_OK)
def delete_all_events(session: Session = Depends(get_session)):
    """Elimina tutti gli eventi e le relative registrazioni."""
    # Svuotiamo prima le registrazioni per evitare conflitti
    registrations = session.exec(select(Registration)).all()
    for reg in registrations:
        session.delete(reg)
        
    # Ora si può procedere con gli eventi in sicurezza
    events = session.exec(select(Event)).all()
    for e in events:
        session.delete(e)
        
    session.commit()
    return {"Tutti gli eventi e le registrazioni associate sono stati eliminati"}


@router_events.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_event(id: int, session: Session = Depends(get_session)):
    """Elimina l'evento indicato ed esegue il cascade sulle registrazioni."""
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    registrations = session.exec(select(Registration).where(Registration.event_id == id)).all()
    for reg in registrations:
        session.delete(reg)

    session.delete(event)
    session.commit()
    return {f"Evento {id} eliminato con successo"}
