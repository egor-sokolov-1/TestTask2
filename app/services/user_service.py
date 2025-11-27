import structlog
from app.repositories.user_repo import UserRepository
from app.integrations.rabbitmq.producer import publish_event
from typing import Optional

logger = structlog.get_logger()

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, data, trace_id: str):
        user = await self.repo.create(data.name, data.surname, data.password)
        await self.repo.session.commit()
        payload = {"event": "user.created", "user_id": user.id, "trace_id": trace_id}
        await publish_event("user.created", payload, trace_id)
        logger.info("user.created", user_id=user.id, trace_id=trace_id)
        return user

    async def list_users(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit, offset)

    async def get_user(self, user_id: int) -> Optional[object]:
        return await self.repo.get(user_id)

    async def update_user(self, user, data, trace_id: str):
        updated = await self.repo.update(user, **data.dict(exclude_unset=True))
        await self.repo.session.commit()
        payload = {"event": "user.updated", "user_id": updated.id, "trace_id": trace_id}
        await publish_event("user.updated", payload, trace_id)
        logger.info("user.updated", user_id=updated.id, trace_id=trace_id)
        return updated

    async def delete_user(self, user, trace_id: str):
        await self.repo.delete(user)
        await self.repo.session.commit()
        payload = {"event": "user.deleted", "user_id": user.id, "trace_id": trace_id}
        await publish_event("user.deleted", payload, trace_id)
        logger.info("user.deleted", user_id=user.id, trace_id=trace_id)
