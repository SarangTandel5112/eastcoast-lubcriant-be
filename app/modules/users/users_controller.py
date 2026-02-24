"""Controller layer for the `users` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users import users_service as service
from app.modules.users.users_dto import UserDTO
from app.modules.users.users_dco import UserDCO, UserUpdateDCO


async def create(session: AsyncSession, data: UserDCO) -> UserDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> UserDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[UserDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: UserUpdateDCO) -> UserDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
