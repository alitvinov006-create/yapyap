from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    g_name: Mapped[str] = mapped_column()
    g_id = mapped_column(BigInteger)
    tg_id = mapped_column(BigInteger)
    tg_name: Mapped[str] = mapped_column()

class Teacher(Base):
    __tablename__ = 'teachers'

    name: Mapped[str] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column()
    tg: Mapped[str] = mapped_column()
    tg_id = mapped_column(BigInteger)
    tg_name: Mapped[str] = mapped_column()

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)