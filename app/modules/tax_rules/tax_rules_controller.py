"""Controller layer for the `tax_rules` module."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tax_rules import tax_rules_service as service
from app.modules.tax_rules.tax_rules_dto import TaxRuleDTO
from app.modules.tax_rules.tax_rules_dco import TaxRuleDCO, TaxRuleUpdateDCO


async def create(session: AsyncSession, data: TaxRuleDCO) -> TaxRuleDTO:
    return await service.create(session, data)


async def get_by_id(session: AsyncSession, record_id: UUID) -> TaxRuleDTO | None:
    return await service.get_by_id(session, record_id)


async def list_all(session: AsyncSession) -> list[TaxRuleDTO]:
    return await service.list_all(session)


async def update(session: AsyncSession, record_id: UUID, data: TaxRuleUpdateDCO) -> TaxRuleDTO | None:
    return await service.update(session, record_id, data)


async def delete_record(session: AsyncSession, record_id: UUID) -> bool:
    return await service.delete_record(session, record_id)
