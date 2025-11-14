from pydantic import BaseModel


class VerifyRecordCommand(BaseModel):
    """Command para verificar un registro de trazabilidad"""
    record_id: int
    verified_by: str
    approved: bool