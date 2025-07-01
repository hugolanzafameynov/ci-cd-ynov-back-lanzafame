from passlib.context import CryptContext
import enum

# Imports SQLAlchemy pour le modèle de base de données
from sqlalchemy import Column, Integer, String, DateTime, Enum, Date
from sqlalchemy.sql import func
from src.database import Base

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

# MODÈLE BASE DE DONNÉES (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Mot de passe hashé
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    birthdate = Column(String(20), nullable=True)  # Format ISO ou YYYY-MM-DD
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    def to_camel_dict(self, public_only=True):
        d = {
            "_id": self.id,
            "username": self.username,
            "role": self.role.value if hasattr(self.role, 'value') else self.role,
            "name": self.name,
            "lastName": self.last_name,
            "createdAt": self.created_at
        }
        if not public_only:
            d.update({
                "birthdate": self.birthdate,
                "city": self.city,
                "postalCode": self.postal_code
            })
        return d

# FONCTIONS UTILITAIRES
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier le mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hasher le mot de passe"""
    return pwd_context.hash(password)
