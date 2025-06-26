from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User, get_password_hash, verify_password, UserRole
from src.middleware.auth import create_access_token

class UserController:
    
    async def get_all_users(self, db: AsyncSession) -> dict:
        """Récupérer tous les utilisateurs (sans les mots de passe)"""
        try:
            # Récupérer tous les utilisateurs
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            # Convertir en dictionnaire (sans mot de passe)
            users_list = []
            for user in users:
                user_dict = {
                    "_id": user.id,  # Utiliser l'ID entier au lieu d'ObjectId
                    "username": user.username,
                    "role": user.role.value,
                    "name": user.name,
                    "lastName": user.last_name,
                    "createdAt": user.created_at
                }
                users_list.append(user_dict)
            
            return {"utilisateurs": users_list}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
            )
    
    async def delete_user(self, user_id: int, current_user: User, db: AsyncSession) -> dict:
        """Supprimer un utilisateur"""
        try:
            # Vérifier que l'admin ne se supprime pas lui-même
            if current_user.id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez pas vous supprimer vous-même."
                )
            
            # Chercher l'utilisateur à supprimer
            result = await db.execute(select(User).where(User.id == user_id))
            user_to_delete = result.scalar_one_or_none()
            
            if not user_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé."
                )
            
            # Supprimer l'utilisateur
            await db.delete(user_to_delete)
            await db.commit()
            
            return {"message": "Utilisateur supprimé."}
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression: {str(e)}"
            )
    
    async def login(self, login_data: dict, db: AsyncSession) -> dict:
        """Authentifier un utilisateur"""
        try:
            username = login_data.get("username")
            password = login_data.get("password")
            
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username et password sont requis"
                )
            
            # Chercher l'utilisateur par username
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utilisateur non trouvé"
                )
            
            if not verify_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mot de passe incorrect"
                )
            
            # Créer le token JWT
            token_data = {"id": str(user.id), "role": user.role.value}
            token = create_access_token(data=token_data)
            
            # Préparer la réponse utilisateur (sans mot de passe)
            user_response = {
                "_id": user.id,
                "username": user.username,
                "role": user.role.value,
                "name": user.name,
                "lastName": user.last_name
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
    
    async def add_user(self, user_data: dict, db: AsyncSession) -> dict:
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
            
            # Vérifier si l'utilisateur existe déjà
            result = await db.execute(select(User).where(User.username == username))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ce nom d'utilisateur existe déjà"
                )
            
            # Hasher le mot de passe
            hashed_password = get_password_hash(password)
            
            # Créer l'utilisateur
            new_user = User(
                username=username,
                password=hashed_password,
                role=UserRole(role),
                name=name,
                last_name=last_name
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)  # Pour récupérer l'ID généré
            
            # Préparer la réponse (sans mot de passe)
            user_response = {
                "_id": new_user.id,
                "username": new_user.username,
                "role": new_user.role.value,
                "name": new_user.name,
                "lastName": new_user.last_name
            }
            
            return {
                "message": "Utilisateur créé",
                "user": user_response
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
            )
