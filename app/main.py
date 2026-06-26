from app.config import config

# NB: do not add imports here!

from pathlib import Path
import os

# ...and here!!

if Path(__file__).parent == Path(os.getcwd()):
    config.root_dir = "."

# You can add imports from here...

from fastapi import FastAPI
from app.routers import frontend
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.data.db import init_database
# Qui importo i 3 nuovi file del backend
from app.routers import events, users, registrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on start
    init_database()
    yield
    # on close


app = FastAPI(lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=config.root_dir / "static"),
    name="static"
)
app.include_router(frontend.router)
#aggiungo i nuovi router per le API del db
app.include_router(events.router)
app.include_router(users.router)
app.include_router(registrations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
