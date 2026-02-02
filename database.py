from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)  # Формат DD.MM.YYYY
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(telegram_id: int):
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

async def create_or_update_user(telegram_id: int, username: str, full_name: str, birth_date: str = None):
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        
        if not user:
            user = User(telegram_id=telegram_id, username=username, full_name=full_name, birth_date=birth_date)
            session.add(user)
        else:
            if birth_date:
                user.birth_date = birth_date
            user.username = username
            user.full_name = full_name
        await session.commit()
        return user
