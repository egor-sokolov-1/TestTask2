from litestar import get, post, put, delete, Litestar, Request, Response
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from app.api.schemas import UserCreate, UserRead, UserUpdate
from app.db.session import get_session
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

route_handlers = []

@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@post("/users", response_model=UserRead, status_code=201, dependencies={"session": Provide(get_session)})
async def create_user(
    data: UserCreate, 
    request: Request, 
    session: AsyncSession 
) -> UserRead:
    trace_id = request.headers.get("x-request-id", None)
    repo = UserRepository(session)
    service = UserService(repo)
    user = await service.create_user(data, trace_id=trace_id or "no-trace")
    return user

@get("/users", response_model=List[UserRead], dependencies={"session": Provide(get_session)})
async def list_users(
    session: AsyncSession  
) -> List[UserRead]:
    repo = UserRepository(session)
    srv = UserService(repo)
    users = await srv.list_users()
    return users

@get("/users/{user_id:int}", response_model=UserRead, dependencies={"session": Provide(get_session)})
async def get_user(
    user_id: int, 
    session: AsyncSession
) -> UserRead:
    repo = UserRepository(session)
    srv = UserService(repo)
    user = await srv.get_user(user_id)
    if not user:
        return Response(status_code=404)
    return user

@put("/users/{user_id:int}", response_model=UserRead, dependencies={"session": Provide(get_session)})
async def update_user(
    user_id: int, 
    data: UserUpdate, 
    request: Request, 
    session: AsyncSession  
) -> UserRead:
    repo = UserRepository(session)
    srv = UserService(repo)
    user = await repo.get(user_id)
    if not user:
        return Response(status_code=404)
    trace_id = request.headers.get("x-request-id", None) or "no-trace"
    updated = await srv.update_user(user, data, trace_id=trace_id)
    return updated

@delete("/users/{user_id:int}", status_code=204, dependencies={"session": Provide(get_session)})
async def delete_user(
    user_id: int, 
    request: Request, 
    session: AsyncSession
) -> None: 
    repo = UserRepository(session)
    srv = UserService(repo)
    user = await repo.get(user_id)
    if not user:
        return Response(status_code=404)
    trace_id = request.headers.get("x-request-id", None) or "no-trace"
    await srv.delete_user(user, trace_id=trace_id)

route_handlers = [health, create_user, list_users, get_user, update_user, delete_user]