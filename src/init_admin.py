import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.user import get_password_hash

load_dotenv()

async def create_admin():
    """Créer un utilisateur admin par défaut"""
    database_url = os.getenv("DATABASE_URL")
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(database_url)
    
    # Extraire le nom de la base de données
    if "?" in database_url:
        db_name = database_url.split("/")[-1].split("?")[0]
    else:
        db_name = database_url.split("/")[-1]
        
    if not db_name:
        db_name = "myapp"
        
    db = client[db_name]
    
    try:
        # Vérifier si l'admin existe déjà
        admin = await db.users.find_one({"username": "loise.fenoll@ynov.com"})
        
        if not admin:
            # Créer l'utilisateur admin
            admin_user = {
                "username": "loise.fenoll@ynov.com",
                "password": get_password_hash("PvdrTAzTeR247sDnAZBr"),
                "role": "admin",
                "name": "Admin",
                "lastName": "User",
                "createdAt": datetime.now()
            }
            
            await db.users.insert_one(admin_user)
            print("Admin user created.")
        else:
            print("Admin user already exists.")
            
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
