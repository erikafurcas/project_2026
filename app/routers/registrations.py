from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.data.db import get_session
from app.models.registration import Registration

router_registrations = APIRouter(prefix="/registrations", tags=["registrations"])


@router_registrations.get("/", response_model=List[Registration])
def get_registrations(session: Session = Depends(get_session)):
    """Restituisce tutte le registrazioni esistenti."""
    return session.exec(select(Registration)).all()


# Api opzionali
@router_registrations.delete("/", status_code=status.HTTP_200_OK)
def delete_registration(username: str, event_id: int, session: Session = Depends(get_session)):
    """Elimina una singola registrazione tramite query parameters."""
    reg = session.exec(
        select(Registration).where(Registration.username == username, Registration.event_id == event_id)
    ).first()

    if not reg:
        raise HTTPException(status_code=404, detail="Registrazione non trovata")

    session.delete(reg)
    session.commit()
    return {"Registrazione eliminata con successo"}
