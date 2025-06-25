from fastapi import HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from src.database import get_database
from src.models.user import User, UserCreate, UserResponse, UserLogin, get_password_hash, verify_password
from src.middleware.auth import create_access_token

class UserController:
    
    async def get_all_users(self) -> dict:
        """Récupérer tous les utilisateurs (sans les mots de passe)"""
        try:
            db = await get_database()
            if db is None:
                from src.database import init_db
                await init_db()
                db = await get_database()
            
            users_cursor = db.users.find({}, {"password": 0})
            users = []
            async for user_doc in users_cursor:
                user_doc["_id"] = str(user_doc["_id"])
                users.append(user_doc)
            
            return {"utilisateurs": users}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
            )
    
    async def delete_user(self, user_id: str, current_user: User) -> dict:
        """Supprimer un utilisateur"""
        try:
            # Vérifier que l'admin ne se supprime pas lui-même
            if str(current_user.id) == user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez pas vous supprimer vous-même."
                )
            
            # Vérifier que l'ID est valide
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID utilisateur invalide"
                )
            
            db = await get_database()
            if db is None:
                from src.database import init_db
                await init_db()
                db = await get_database()
            
            result = await db.users.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé."
                )
            
            return {"message": "Utilisateur supprimé."}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression: {str(e)}"
            )
    
    async def login(self, login_data: dict) -> dict:
        """Authentifier un utilisateur"""
        try:
            username = login_data.get("username")
            password = login_data.get("password")
            
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username et password sont requis"
                )
            
            db = await get_database()
            if db is None:
                from src.database import init_db
                await init_db()
                db = await get_database()
            
            user_doc = await db.users.find_one({"username": username})
            
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utilisateur non trouvé"
                )
            
            if not verify_password(password, user_doc["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mot de passe incorrect"
                )
            
            # Créer le token JWT
            token_data = {"id": str(user_doc["_id"]), "role": user_doc["role"]}
            token = create_access_token(data=token_data)
            
            # Préparer la réponse utilisateur (sans mot de passe)
            user_response = {
                "_id": str(user_doc["_id"]),
                "username": user_doc["username"],
                "role": user_doc["role"],
                "name": user_doc.get("name"),
                "lastName": user_doc.get("lastName")
            }
            
            return {
                "message": "Connexion réussie",
                "token": token,
                "user": user_response
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la connexion: {str(e)}"
            )
    
    async def add_user(self, user_data: dict) -> dict:
        """Créer un nouvel utilisateur"""
        try:
            username = user_data.get("username")
            password = user_data.get("password")
            role = user_data.get("role", "user")
            name = user_data.get("name")
            last_name = user_data.get("lastName")
            
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username et password sont requis"
                )
            
            db = await get_database()
            if db is None:
                from src.database import init_db
                await init_db()
                db = await get_database()
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = await db.users.find_one({"username": username})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ce nom d'utilisateur existe déjà"
                )
            
            # Hasher le mot de passe
            hashed_password = get_password_hash(password)
            
            # Créer le document utilisateur
            user_doc = {
                "username": username,
                "password": hashed_password,
                "role": role,
                "name": name,
                "lastName": last_name,
                "createdAt": datetime.now()
            }
            
            # Insérer l'utilisateur
            result = await db.users.insert_one(user_doc)
            
            # Préparer la réponse (sans mot de passe)
            user_response = {
                "_id": str(result.inserted_id),
                "username": username,
                "role": role,
                "name": name,
                "lastName": last_name
            }
            
            return {
                "message": "Utilisateur créé",
                "user": user_response
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
            )
