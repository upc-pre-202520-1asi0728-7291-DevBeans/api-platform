from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from coffee_lot_management.domain.model.aggregates.coffee_lot import CoffeeLot, LotStatus, CoffeeVariety, \
    ProcessingMethod
from coffee_lot_management.domain.model.queries.get_coffee_lot_by_id_query import GetCoffeeLotByIdQuery
from coffee_lot_management.domain.model.queries.get_coffee_lots_by_producer_query import GetCoffeeLotsByProducerQuery
from coffee_lot_management.domain.model.queries.get_lot_traceability_query import GetLotTraceabilityQuery
from coffee_lot_management.domain.model.queries.search_coffee_lots_query import SearchCoffeeLotsQuery
from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import \
    CoffeeLotRepository


class CoffeeLotQueryService:
    """Servicio de queries para CoffeeLot"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = CoffeeLotRepository(db)

    def handle_get_coffee_lot_by_id(self, query: GetCoffeeLotByIdQuery) -> CoffeeLot:
        """Recupera lote específico con información completa"""
        coffee_lot = self.repository.find_by_id(query.lot_id)
        if not coffee_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coffee lot not found"
            )
        return coffee_lot

    def handle_get_coffee_lots_by_producer(self, query: GetCoffeeLotsByProducerQuery) -> list[type[CoffeeLot]]:
        """Lista los lotes filtrados por productor y criterios opcionales"""
        # Obtener todos los lotes del productor primero
        lots = self.repository.find_by_producer_id(query.producer_id)

        # Filtrar por estado si se especifica
        if query.status:
            try:
                status_enum = LotStatus[query.status.upper()]
                lots = [lot for lot in lots if lot.status == status_enum]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {query.status}"
                )

        # Filtrar por año de cosecha si se especifica
        if query.harvest_year:
            lots = [lot for lot in lots if lot.harvest_date.year == query.harvest_year]

        return lots

    def handle_search_coffee_lots(self, query: SearchCoffeeLotsQuery) -> list[type[CoffeeLot]]:
        """Búsqueda avanzada de lotes con múltiples criterios"""
        base_query = self.db.query(CoffeeLot)

        # Aplicar filtros
        if query.variety:
            try:
                variety_enum = CoffeeVariety[query.variety.upper()]
                base_query = base_query.filter(CoffeeLot.coffee_variety == variety_enum)
            except KeyError:
                pass

        # FIX: Agregado el filtro de processing_method que faltaba
        if query.processing_method:
            try:
                processing_enum = ProcessingMethod[query.processing_method.upper()]
                base_query = base_query.filter(CoffeeLot.processing_method == processing_enum)
            except KeyError:
                pass

        if query.status:
            try:
                status_enum = LotStatus[query.status.upper()]
                base_query = base_query.filter(CoffeeLot.status == status_enum)
            except KeyError:
                pass

        # Filtros de fecha para harvest_date
        if query.start_date:
            base_query = base_query.filter(CoffeeLot.harvest_date >= query.start_date)

        if query.end_date:
            base_query = base_query.filter(CoffeeLot.harvest_date <= query.end_date)

        return base_query.all()

    def handle_get_lot_traceability(self, query: GetLotTraceabilityQuery) -> Optional[CoffeeLot]:
        """Recupera información completa para trazabilidad"""
        coffee_lot = self.repository.find_by_lot_number(query.lot_number)
        if not coffee_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coffee lot not found"
            )
        return coffee_lot