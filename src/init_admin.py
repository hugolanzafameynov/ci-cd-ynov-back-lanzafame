import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.user import get_password_hash, UserRole, User
from src.database import Base

async def create_admin():
    """Créer un utilisateur admin par défaut"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Créer le moteur et les tables
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        try:
            # Vérifier si l'admin existe déjà
            result = await session.execute(
                select(User).where(User.username == "loise.fenoll@ynov.com")
            )
            admin = result.scalar_one_or_none()
            
            if not admin:
                # Créer l'utilisateur admin
                admin_user = User(
                    username="loise.fenoll@ynov.com",
                    password=get_password_hash("PvdrTAzTeR247sDnAZBr"),
                    role=UserRole.admin,
                    name="Admin",
                    last_name="User"
                )
                
                session.add(admin_user)
                await session.commit()
                print("Admin user created successfully.")
            else:
                print("Admin user already exists.")
                
        except Exception as e:
            print(f"Error creating admin user: {e}")
            await session.rollback()
        finally:
            await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())
