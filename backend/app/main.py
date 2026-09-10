from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.api import auth, users, favorites, football

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Football QA API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(users.router); app.include_router(favorites.router); app.include_router(football.router)
@app.get("/health")
def health(): return {"status":"ok"}
