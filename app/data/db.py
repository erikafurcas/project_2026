from app.models.event import Event  # aggiunto
from app.models.user import User  # aggiunto
from app.models.registration import Registration  # NOQA
from sqlmodel import create_engine, SQLModel, Session, select
from typing import Annotated
from fastapi import Depends
import os
from faker import Faker
from app.config import config

# TODO: remember to import all the DB models here

from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration

sqlite_file_name = config.root_dir / "data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def init_database() -> None:
    ds_exists = os.path.isfile(sqlite_file_name)
    SQLModel.metadata.create_all(engine)
    if not ds_exists:
        f = Faker("it_IT")
        with Session(engine) as session:
            # TODO: (optional) initialize the database with fake data
            ...
def init_database() -> None:
    ds_exists = os.path.isfile(sqlite_file_name)
    SQLModel.metadata.create_all(engine)
    
    # Se il database non esisteva (primo avvio), lo popoliamo
    if not ds_exists:
        f = Faker("it_IT")
        with Session(engine) as session:
            # 1. Creazione di alcuni utenti di esempio
            users = []
            for _ in range(5):
                new_user = User(
                    username=f.user_name(),
                    name=f.name(),
                    email=f.email()
                )
                session.add(new_user)
                users.append(new_user)
            
            # 2. Creazione di alcuni eventi di esempio
            events = []
            for _ in range(3):
                new_event = Event(
                    title=f.sentence(nb_words=3),
                    description=f.text(max_nb_chars=100),
                    date=f.date_time_between(start_date='now', end_date='+1y'), # Usa datetime [4, 5]
                    location=f.city()
                )
                session.add(new_event)
                events.append(new_event)
            
            # Salviamo utenti ed eventi per poter creare le registrazioni
            session.commit()

            # 3. (Opzionale) Creazione di alcune registrazioni casuali
            for user in users:
                # Registra ogni utente a un evento a caso
                import random
                event = random.choice(events)
                registration = Registration(username=user.username, event_id=event.id)
                session.add(registration)
            
            session.commit()
            print("Database inizializzato con successo con dati di esempio!")

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
