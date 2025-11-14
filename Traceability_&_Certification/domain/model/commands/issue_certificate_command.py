from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any


class IssueCertificateCommand(BaseModel):
    """Command para emitir un certificado digital"""
    traceability_record_id: int
    coffee_lot_id: int
    certificate_type: str
    title: str
    description: Optional[str] = None
    issue_date: date
    expiry_date: Optional[date] = None
    issuing_authority: str
    issuing_authority_contact: Optional[str] = None
    certification_criteria: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None