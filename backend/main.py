from fastapi import FastAPI
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from routers.transport import router as transport
from routers.task import router as task

Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost:5173",  # React par défaut
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # ← ici : les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure le routeur des prêts bancaires
app.include_router(transport)
app.include_router(task)

@app.get("/")
async def root_status():
    return {
        "status": "ok",
        "database": "ready",
        "message": "Backend is running smoothly"
    }
