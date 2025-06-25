import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import asyncio

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def init_db():
    """Initialiser la connexion à MongoDB"""
    database_url = os.getenv("DATABASE_URL", "mongodb://root:example@mongodb:27017/myapp?authSource=admin")
    
    try:
        # Créer le client MongoDB
        db.client = AsyncIOMotorClient(database_url)
        
        # Test de la connexion
        await db.client.admin.command('ping')
        print("Connected to MongoDB")
        
        # Extraire le nom de la base de données de l'URL
        if "?" in database_url:
            db_name = database_url.split("/")[-1].split("?")[0]
        else:
            db_name = database_url.split("/")[-1]
            
        if not db_name:
            db_name = "myapp"
            
        db.database = db.client[db_name]
        
    except ConnectionFailure as e:
        print(f"MongoDB connection error: {e}")
        raise e

async def close_db():
    """Fermer la connexion à MongoDB"""
    if db.client:
        db.client.close()
