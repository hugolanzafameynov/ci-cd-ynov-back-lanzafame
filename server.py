from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv()

from src.init_admin import create_admin
from src.database import init_db, get_async_session
from src.models.user import User
from src.controllers.user_controller import UserController
from src.middleware.auth import admin_required, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await create_admin()
    yield

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
@app.get("/")
async def root():
    return {"message": "API Backend Ynov - Python FastAPI"}

@app.post("/v1/users", status_code=status.HTTP_201_CREATED)
async def add_user(user_data: dict, db: AsyncSession = Depends(get_async_session)):
    """Créer un nouvel utilisateur"""
    return await user_controller.add_user(user_data, db)

@app.post("/v1/login")
async def login(login_data: dict, db: AsyncSession = Depends(get_async_session)):
    """Authentification utilisateur"""
    return await user_controller.login(login_data, db)

@app.get("/v1/users")
async def get_all_users(db: AsyncSession = Depends(get_async_session)):
    """Récupérer tous les utilisateurs (infos de base)"""
    return await user_controller.get_all_users(db)

# Route protégée : admin uniquement
@app.get("/v1/users-sensitive")
async def get_all_users_sensitive(current_user: User = Depends(admin_required), db: AsyncSession = Depends(get_async_session)):
    """Récupérer la liste des utilisateurs avec informations sensibles"""
    return await user_controller.get_all_users_sensitive(current_user, db)
    
@app.delete("/v1/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(admin_required), db: AsyncSession = Depends(get_async_session)):
    """Supprimer un utilisateur"""
    return await user_controller.delete_user(user_id, current_user, db)

# Route protégée : utilisateur connecté
@app.get("/v1/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Récupérer les informations du profil utilisateur connecté"""
    return {
        "_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value,
        "name": current_user.name,
        "lastName": current_user.last_name,
        "birthdate": current_user.birthdate.isoformat() if current_user.birthdate else None,
        "city": current_user.city,
        "postalCode": current_user.postal_code,
        "createdAt": current_user.created_at
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4000, reload=True)
