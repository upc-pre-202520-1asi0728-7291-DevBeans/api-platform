from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class RegisterTraceabilityCommand(BaseModel):
    """Command para registrar un evento de trazabilidad"""
    coffee_lot_id: int
    record_type: str
    event_description: str
    event_date: datetime
    location: Optional[str] = None
    responsible_person: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None