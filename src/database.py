import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration du moteur avec options pour Aiven
engine_kwargs = {
    "echo": True,
    "pool_pre_ping": True,  # Vérifie la connexion avant utilisation
    "pool_recycle": 3600,   # Recycle les connexions après 1h
}

# Création du moteur SQLAlchemy async
engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Fonctions utilitaires
async def init_db():
    """Initialiser la base de données"""
    try:
        # Importer les modèles pour s'assurer qu'ils sont enregistrés
        from src.models.user import User  # Import nécessaire pour créer les tables
        
        # Créer les tables si elles n'existent pas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Connected to MySQL database and tables created")
        
    except Exception as e:
        print(f"Database connection error: {e}")
        raise e

async def close_db():
    """Fermer la connexion à la base de données"""
    await engine.dispose()

async def get_async_session():
    """Obtenir une session async SQLAlchemy"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
