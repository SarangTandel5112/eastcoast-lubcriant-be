"""Controller layer for the `dealer_addresses` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dealer_addresses import dealer_addresses_service as service
from app.modules.dealer_addresses.dealer_addresses_dto import DealerAddressDTO
from app.modules.dealer_addresses.dealer_addresses_dco import DealerAddressDCO, DealerAddressUpdateDCO


async def create(session: AsyncSession, data: DealerAddressDCO) -> DealerAddressDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> DealerAddressDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[DealerAddressDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: DealerAddressUpdateDCO) -> DealerAddressDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
