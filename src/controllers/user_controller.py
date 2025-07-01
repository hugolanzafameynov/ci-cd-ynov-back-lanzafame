from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User, get_password_hash, verify_password, UserRole
from src.middleware.auth import create_access_token

class UserController:
    async def get_all_users(self, db: AsyncSession) -> dict:
        """Récupérer la liste de tous les utilisateurs (infos de base, accessible à tous)"""
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()
            users_list = [user.to_camel_dict() for user in users]
            return {"utilisateurs": users_list}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
            )

    async def delete_user(self, user_id: int, current_user: User, db: AsyncSession) -> dict:
        """Supprimer un utilisateur"""
        try:
            if current_user.id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez pas vous supprimer vous-même."
                )
            result = await db.execute(select(User).where(User.id == user_id))
            user_to_delete = result.scalar_one_or_none()
            if not user_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé."
                )
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
            token_data = {"id": str(user.id), "role": user.role.value}
            token = create_access_token(data=token_data)
            user_response = user.to_camel_dict()
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
            birthdate = user_data.get("birthdate")
            city = user_data.get("city")
            postal_code = user_data.get("postalCode")
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username et password sont requis"
                )
            result = await db.execute(select(User).where(User.username == username))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ce nom d'utilisateur existe déjà"
                )
            hashed_password = get_password_hash(password)
            new_user = User(
                username=username,
                password=hashed_password,
                role=UserRole(role),
                name=name,
                last_name=last_name,
                birthdate=birthdate,
                city=city,
                postal_code=postal_code
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user_response = new_user.to_camel_dict()
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
    
    async def get_all_users_sensitive(self, current_user: User, db: AsyncSession) -> dict:
        """Récupérer la liste de tous les utilisateurs avec informations sensibles (admin uniquement)"""
        if current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé à l'administrateur."
            )
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()
            users_list = [user.to_camel_dict(public_only=False) for user in users]
            return {"utilisateurs": users_list}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
            )
