from database.models import async_session
from database.models import User, Teacher
from sqlalchemy import select

async def set_user(tg_id, tg_name, g_name, g_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(
                User(
                    tg_id=tg_id,
                    tg_name=tg_name,
                    g_name=g_name,
                    g_id=g_id
                )
            )
            await session.commit()

async def get_info():
    async with async_session() as session:
        result = await session.execute(
            select(User.tg_id, User.tg_name, User.g_name, User.g_id)
        )
        return result.all()

async def get_teachers():
    async with async_session() as session:
        result = await session.execute(
            select(Teacher.name, Teacher.subject, Teacher.tg, Teacher.number)
        )
        return result.all()

async def get_contacts():
    async with async_session() as session:
        result = await session.execute(
            select(
                Teacher.name,
                Teacher.subject,
                Teacher.tg,
                Teacher.number
            )
        )

        return result.all()


async def get_users_from_group(group):
    stmt = select(User.tg_id).where(User.g_name == group)
    async with async_session() as session:
        result = await session.scalars(stmt)
        return result.all()