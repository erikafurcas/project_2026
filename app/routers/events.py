from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

# Import dei modelli e della sessione del database
from app.models.event import Event
from app.data.db import get_session

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.get("", response_model=List[Event])
def get_events(session: Session = Depends(get_session)):
    """
    Restituisce la lista di tutti gli eventi esistenti.
    Risposta: 200 OK con l'elenco degli eventi.
    """
    events = session.exec(select(Event)).all()
    return events

@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: Event, session: Session = Depends(get_session)):
    """
    Crea un nuovo evento.
    
    Risolve il problema di SQLite intercettando il payload se la data 
    viene inviata come stringa e convertendola manualmente in un oggetto datetime.
    """
    # Fix per il bug di SQLite rigid sulle tipologie di dato (conversione esplicita)
    if hasattr(event, "date") and isinstance(event.date, str):
        event.date = datetime.fromisoformat(event.date)
        
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.get("/{id}", response_model=Event)
def get_event_by_id(id: int, session: Session = Depends(get_session)):
    """
    Restituisce l'evento con l'id indicato.
    Risposta: 200 OK se trovato, 404 Not Found se l'evento non esiste.
    """
    db_event = session.get(Event, id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return db_event

@router.put("/{id}", response_model=Event)
def update_event(id: int, event_data: Event, session: Session = Depends(get_session)):
    """
    Aggiorna l'evento con l'id indicato.
    
    Verifica ed effettua la conversione manuale della data nel caso in cui 
    venga passata come stringa nel corpo della richiesta (evitando il crash del server).
    Risposta: 200 OK se aggiornato, 404 Not Found se l'evento non esiste.
    """
    db_event = session.get(Event, id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    # Estrae i dati inviati escludendo i valori non impostati
    data = event_data.dict(exclude_unset=True)
    for key, value in data.items():
        if key == "id":
            continue
        # Intercetta e converte la stringa in datetime per SQLite
        if key == "date" and isinstance(value, str):
            value = datetime.fromisoformat(value)
        setattr(db_event, key, value)
        
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.delete("", status_code=status.HTTP_200_OK)
def delete_all_events(session: Session = Depends(get_session)):
    """
    (Opzionale) Elimina tutti gli eventi dal database.
    
    Esegue prima una pulizia preventiva delle registrazioni associate per evitare 
    blocchi o eccezioni dovute ai vincoli di Foreign Key in SQLite.
    """
    # Svuota prima la tabella delle registrazioni collegate per sicurezza (vincoli FK)
    # Nota: Sostituisci "registration" con il nome esatto della tua tabella se differisce
    session.execute("DELETE FROM registration")
    
    # Elimina tutti gli eventi
    events = session.exec(select(Event)).all()
    for e in events:
        session.delete(e)
        
    session.commit()
    return {"message": "Tutti gli eventi e le relative registrazioni sono stati eliminati"}

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_event_by_id(id: int, session: Session = Depends(get_session)):
    """
    (Opzionale) Elimina l'evento con l'id indicato.
    
    Elimina a cascata (cascade) tutte le registrazioni associate a questo specifico 
    evento prima di rimuoverlo per prevenire violazioni di vincoli relazionali.
    Risposta: 200 OK, 404 Not Found se l'evento non esiste.
    """
    db_event = session.get(Event, id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
        
    # Eliminazione preventiva mirata delle registrazioni legate a questo ID evento
    session.execute(f"DELETE FROM registration WHERE event_id = {id}")
    
    # Eliminazione dell'evento reale
    session.delete(db_event)
    session.commit()
    return {"message": f"Evento con ID {id} e registrazioni associate eliminati con successo"}
