from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.data.db import get_session
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration
from datetime import datetime

# Creiamo il router specifico per ogni evento
router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[Event])
def get_events(session: Session = Depends(get_session)):
    """Restituisce la lista di tutti gli eventi esistenti."""
    return session.exec(select(Event)).all()


@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: Event, session: Session = Depends(get_session)):
    """Crea un nuovo evento."""
    # Forza l'errore 422 se un campo stringa ha un tipo errato (es. un intero)
    if not isinstance(event.title, str) or not isinstance(event.description, str) or not isinstance(event.location, str):
        raise HTTPException(status_code=422, detail="I campi di testo devono essere stringhe")

    # Gestione robusta del parsing o della mancanza della data
    if event.date is None:
        raise HTTPException(status_code=422, detail="Data mancante")
        
    if isinstance(event.date, str):
        try:
            event.date = datetime.fromisoformat(event.date)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="Formato data non valido")

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("/{id}", response_model=Event)
def get_event(id: int, session: Session = Depends(get_session)):
    """Restituisce l'evento con l'id indicato."""
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


@router.put("/{id}", response_model=Event)
def update_event(id: int, updated_event: Event, session: Session = Depends(get_session)):
    """Aggiorna un evento esistente."""
    # Controllo tipo dei campi
    if not isinstance(updated_event.title, str) or not isinstance(updated_event.description, str) or not isinstance(updated_event.location, str):
        raise HTTPException(status_code=422, detail="I campi di testo devono essere stringhe")

    db_event = session.get(Event, id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    if isinstance(updated_event.date, str):
        try:
            updated_event.date = datetime.fromisoformat(updated_event.date)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="Formato data non valido")

    data = updated_event.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key != "id":
            setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.post("/{id}/register", status_code=status.HTTP_201_CREATED)
def register_to_event(id: int, user_data: User, session: Session = Depends(get_session)):
    """Registra un utente a un evento. Se l'utente non esiste, lo crea."""
    # Validazione del tipo per lo username dell'utente (evita che passi un intero)
    if not isinstance(user_data.username, str) or not isinstance(user_data.name, str):
        raise HTTPException(status_code=422, detail="I campi dell'utente devono essere validi")

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
        session.refresh(registration)
        return registration  # Restituisce l'oggetto registrazione come richiesto dal test format

    return existing_reg


# API Opzionali

@router.delete("/", status_code=status.HTTP_200_OK)
def delete_all_events(session: Session = Depends(get_session)):
    """Elimina tutti gli eventi e le relative registrazioni."""
    registrations = session.exec(select(Registration)).all()
    for reg in registrations:
        session.delete(reg)
        
    events = session.exec(select(Event)).all()
    for e in events:
        session.delete(e)
        
    session.commit()
    return {"message": "Tutti gli eventi e le registrazioni associate sono stati eliminati"}


@router.delete("/{id}", status_code=status.HTTP_200_OK)
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
    return {"message": f"Evento {id} eliminato con successo"}
