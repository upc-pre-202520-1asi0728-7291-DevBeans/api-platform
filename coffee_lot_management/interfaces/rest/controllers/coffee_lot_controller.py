from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from coffee_lot_management.application.internal.commandservices.coffee_lot_command_service import \
    CoffeeLotCommandService
from coffee_lot_management.application.internal.queryservices.coffee_lot_query_service import CoffeeLotQueryService
from coffee_lot_management.domain.model.commands.change_lot_status_command import ChangeLotStatusCommand
from coffee_lot_management.domain.model.commands.delete_coffee_lot_command import DeleteCoffeeLotCommand
from coffee_lot_management.domain.model.commands.register_coffee_lot_command import RegisterCoffeeLotCommand
from coffee_lot_management.domain.model.commands.update_coffee_lot_command import UpdateCoffeeLotCommand
from coffee_lot_management.domain.model.queries.get_coffee_lot_by_id_query import GetCoffeeLotByIdQuery
from coffee_lot_management.domain.model.queries.get_coffee_lots_by_producer_query import GetCoffeeLotsByProducerQuery
from coffee_lot_management.domain.model.queries.search_coffee_lots_query import SearchCoffeeLotsQuery
from shared.domain.database import get_db

router = APIRouter(prefix="/api/v1/coffee-lots", tags=["Coffee Lot Management"])


# Enums para validación en la API
class CoffeeVarietyEnum(str, Enum):
    TYPICA = "TYPICA"
    CATURRA = "CATURRA"
    BOURBON = "BOURBON"
    GEISHA = "GEISHA"
    SL28 = "SL28"
    SL34 = "SL34"
    CASTILLO = "CASTILLO"
    COLOMBIA = "COLOMBIA"


class ProcessingMethodEnum(str, Enum):
    WASHED = "WASHED"
    NATURAL = "NATURAL"
    HONEY = "HONEY"
    SEMI_WASHED = "SEMI_WASHED"


class LotStatusEnum(str, Enum):
    REGISTERED = "REGISTERED"
    PROCESSING = "PROCESSING"
    CLASSIFIED = "CLASSIFIED"
    CERTIFIED = "CERTIFIED"
    SHIPPED = "SHIPPED"


# Resources
class RegisterCoffeeLotResource(BaseModel):
    """Resource para registrar nuevo lote"""
    producer_id: int
    harvest_date: date
    coffee_variety: CoffeeVarietyEnum  # Usa el Enum
    quantity: float = Field(gt=0)
    processing_method: ProcessingMethodEnum  # Usa el Enum
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None
    soil_type: Optional[str] = None
    climate_zone: Optional[str] = None
    farm_section: Optional[str] = None


class CoffeeLotResource(BaseModel):
    """Resource para respuesta de lote"""
    id: int
    lot_number: str
    producer_id: int
    harvest_date: date
    coffee_variety: str
    quantity: float
    status: str
    processing_method: str
    altitude: Optional[float]
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateCoffeeLotResource(BaseModel):
    """Resource para actualizar lote"""
    quantity: Optional[float] = Field(gt=0, default=None)
    processing_method: Optional[ProcessingMethodEnum] = None
    altitude: Optional[float] = None
    soil_type: Optional[str] = None
    climate_zone: Optional[str] = None


class LotStatusChangeResource(BaseModel):
    """Resource para cambio de estado"""
    new_status: LotStatusEnum  # Usa el Enum
    change_reason: Optional[str] = None


# Endpoints
@router.post("", response_model=CoffeeLotResource, status_code=status.HTTP_201_CREATED)
async def register_coffee_lot(
        resource: RegisterCoffeeLotResource,
        db: Session = Depends(get_db)
):
    """Registra un nuevo lote de café"""
    command = RegisterCoffeeLotCommand(**resource.model_dump())
    command_service = CoffeeLotCommandService(db)
    coffee_lot = command_service.handle_register_coffee_lot(command)
    return CoffeeLotResource.model_validate(coffee_lot)


@router.get("/{lot_id}", response_model=CoffeeLotResource)
async def get_coffee_lot(
        lot_id: int,
        db: Session = Depends(get_db)
):
    """Obtiene información de un lote específico"""
    query = GetCoffeeLotByIdQuery(lot_id=lot_id)
    query_service = CoffeeLotQueryService(db)
    coffee_lot = query_service.handle_get_coffee_lot_by_id(query)
    return CoffeeLotResource.model_validate(coffee_lot)


@router.put("/{lot_id}", response_model=CoffeeLotResource)
async def update_coffee_lot(
        lot_id: int,
        resource: UpdateCoffeeLotResource,
        db: Session = Depends(get_db)
):
    """Actualiza información de un lote"""
    command = UpdateCoffeeLotCommand(lot_id=lot_id, **resource.model_dump())
    command_service = CoffeeLotCommandService(db)
    coffee_lot = command_service.handle_update_coffee_lot(command)
    return CoffeeLotResource.model_validate(coffee_lot)


@router.delete("/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coffee_lot(
        lot_id: int,
        deletion_reason: str = Query(..., description="Razón de la eliminación"),
        db: Session = Depends(get_db)
):
    """Elimina un lote de café"""
    command = DeleteCoffeeLotCommand(lot_id=lot_id, deletion_reason=deletion_reason)
    command_service = CoffeeLotCommandService(db)
    command_service.handle_delete_coffee_lot(command)
    return None


@router.patch("/{lot_id}/status", response_model=CoffeeLotResource)
async def change_lot_status(
        lot_id: int,
        resource: LotStatusChangeResource,
        db: Session = Depends(get_db)
):
    """Cambia el estado de un lote"""
    command = ChangeLotStatusCommand(
        lot_id=lot_id,
        new_status=resource.new_status,
        change_reason=resource.change_reason
    )
    command_service = CoffeeLotCommandService(db)
    coffee_lot = command_service.handle_change_lot_status(command)
    return CoffeeLotResource.model_validate(coffee_lot)


@router.get("/producer/{producer_id}", response_model=List[CoffeeLotResource])
async def get_lots_by_producer(
        producer_id: int,
        producer_status: Optional[LotStatusEnum] = Query(None, description="Filtrar por estado"),
        harvest_year: Optional[int] = Query(None, description="Filtrar por año de cosecha"),
        db: Session = Depends(get_db)
):
    """Obtiene todos los lotes de un productor"""
    query = GetCoffeeLotsByProducerQuery(
        producer_id=producer_id,
        status=producer_status.value if producer_status else None,
        harvest_year=harvest_year
    )
    query_service = CoffeeLotQueryService(db)
    lots = query_service.handle_get_coffee_lots_by_producer(query)
    return [CoffeeLotResource.model_validate(lot) for lot in lots]


@router.get("/search/advanced", response_model=List[CoffeeLotResource])
async def search_coffee_lots(
        variety: Optional[CoffeeVarietyEnum] = Query(None, description="Filtrar por variedad de café"),
        processing_method: Optional[ProcessingMethodEnum] = Query(None, description="Filtrar por método de procesamiento"),
        coffee_status: Optional[LotStatusEnum] = Query(None, description="Filtrar por estado del lote"),
        start_date: Optional[date] = Query(None, description="Fecha de cosecha desde (inclusive)"),
        end_date: Optional[date] = Query(None, description="Fecha de cosecha hasta (inclusive)"),
        db: Session = Depends(get_db)
):
    """Búsqueda avanzada de lotes de café con múltiples filtros"""
    query = SearchCoffeeLotsQuery(
        variety=variety.value if variety else None,
        processing_method=processing_method.value if processing_method else None,
        status=coffee_status.value if coffee_status else None,
        start_date=start_date,
        end_date=end_date
    )
    query_service = CoffeeLotQueryService(db)
    lots = query_service.handle_search_coffee_lots(query)
    return [CoffeeLotResource.model_validate(lot) for lot in lots]