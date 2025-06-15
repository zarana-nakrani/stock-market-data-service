from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

#SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

#sync engine for migrations
sync_engine = create_engine(SQLALCHEMY_DATABASE_URL)

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

#SessionLocal class for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
#Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session.
    Yields a session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """
    Dependency that provides an asynchronous database session.
    Yields a session and ensures it is closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
        await session.close()

# Create all tables in the database
async def init_db():
    """
    Initialize the database by creating all tables.
    This should be called once at the start of the application.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully!")

