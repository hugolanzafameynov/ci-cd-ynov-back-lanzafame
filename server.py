from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from src.database import init_db
from src.models.user import User
from src.controllers.user_controller import UserController
from src.middleware.auth import get_current_user, get_current_admin_user

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (si nécessaire)

app = FastAPI(
    title="API Backend Ynov",
    description="API REST pour la gestion des utilisateurs",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance du contrôleur utilisateur
user_controller = UserController()

# Routes publiques
@app.post("/v1/users", status_code=status.HTTP_201_CREATED)
async def add_user(user_data: dict):
    """Créer un nouvel utilisateur (route publique)"""
    return await user_controller.add_user(user_data)

@app.post("/v1/login")
async def login(login_data: dict):
    """Authentification utilisateur"""
    return await user_controller.login(login_data)

# Routes protégées (admin seulement)
@app.get("/v1/users")
async def get_all_users(current_user: User = Depends(get_current_admin_user)):
    """Récupérer tous les utilisateurs (admin uniquement)"""
    return await user_controller.get_all_users()

@app.delete("/v1/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_current_admin_user)):
    """Supprimer un utilisateur (admin uniquement)"""
    return await user_controller.delete_user(user_id, current_user)

@app.get("/")
async def root():
    return {"message": "API Backend Ynov - Python FastAPI"}

# Handler pour Vercel
handler = app

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4000, reload=True)
