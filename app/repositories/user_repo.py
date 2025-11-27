from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from typing import List, Optional

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, surname: str, password: str) -> User:
        user = User(name=name, surname=surname, password=password)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, user_id: int) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        q = select(User).limit(limit).offset(offset)
        res = await self.session.execute(q)
        return res.scalars().all()

    async def update(self, user: User, **kwargs) -> User:
        for k, v in kwargs.items():
            setattr(user, k, v)
        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        return
