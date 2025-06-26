from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv()

from src.database import init_db, get_async_session
from src.models.user import User
from src.controllers.user_controller import UserController
from src.middleware.auth import admin_required

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Ne pas initialiser la DB sur Vercel au startup
    # await init_db()  # Commenté pour éviter les timeouts sur Vercel
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
async def add_user(user_data: dict, db: AsyncSession = Depends(get_async_session)):
    """Créer un nouvel utilisateur (route publique)"""
    return await user_controller.add_user(user_data, db)

@app.post("/v1/login")
async def login(login_data: dict, db: AsyncSession = Depends(get_async_session)):
    """Authentification utilisateur"""
    return await user_controller.login(login_data, db)

# Routes protégées (admin seulement)
@app.get("/v1/users")
async def get_all_users(current_user: User = Depends(admin_required), db: AsyncSession = Depends(get_async_session)):
    """Récupérer tous les utilisateurs (admin uniquement)"""
    return await user_controller.get_all_users(db)

@app.delete("/v1/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(admin_required), db: AsyncSession = Depends(get_async_session)):
    """Supprimer un utilisateur (admin uniquement)"""
    return await user_controller.delete_user(user_id, current_user, db)

@app.get("/")
async def root():
    return {"message": "API Backend Ynov - Python FastAPI"}

# Handler pour Vercel
app_handler = app

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4000, reload=True)
