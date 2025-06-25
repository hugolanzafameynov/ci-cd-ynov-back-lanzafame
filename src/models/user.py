from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext
from bson import ObjectId

# Configuration pour le hachage des mots de passe avec bcrypt uniquement
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "username": "test",
                "password": "test123",
                "role": "user",
                "name": "test",
                "lastName": "lasttest"
            }
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: str = Field(default="user", pattern="^(admin|user)$")
    name: Optional[str] = None
    last_name: Optional[str] = Field(None, alias="lastName")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

class UserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: Optional[str] = Field(default="user", pattern="^(admin|user)$")
    name: Optional[str] = None
    last_name: Optional[str] = Field(None, alias="lastName")

class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(alias="_id")
    username: str
    role: str
    name: Optional[str] = None
    last_name: Optional[str] = Field(None, alias="lastName")
    created_at: datetime = Field(alias="createdAt")

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier le mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hasher le mot de passe"""
    return pwd_context.hash(password)
