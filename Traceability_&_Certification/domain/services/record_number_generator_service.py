from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


class RecordNumberGeneratorService:
    """
    Servicio para generar números únicos de registro de trazabilidad
    Patrón: TRC-YYYY-MM-NNNN
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_record_number(self) -> str:
        """
        Genera un número único de registro
        Formato: TRC-YYYY-MM-NNNN
        """
        now = datetime.now()
        year = now.year
        month = now.month

        # Contar registros del mes actual usando text()
        sql_query = text("""
            SELECT COUNT(*) FROM traceability_records 
            WHERE EXTRACT(YEAR FROM created_at) = :year
            AND EXTRACT(MONTH FROM created_at) = :month
        """)

        result = self.db.execute(sql_query, {"year": year, "month": month})
        count = result.scalar()

        sequential = (count or 0) + 1
        record_number = f"TRC-{year}-{month:02d}-{sequential:04d}"

        # Verificar unicidad usando text()
        check_query = text("""
            SELECT COUNT(*) FROM traceability_records 
            WHERE record_number = :record_number
        """)

        result = self.db.execute(check_query, {"record_number": record_number})
        exists = result.scalar()

        while exists > 0:
            sequential += 1
            record_number = f"TRC-{year}-{month:02d}-{sequential:04d}"
            result = self.db.execute(check_query, {"record_number": record_number})
            exists = result.scalar()

        return record_number


class CertificateNumberGeneratorService:
    """
    Servicio para generar números únicos de certificados
    Patrón: CERT-TYPE-YYYY-NNNN
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_certificate_number(self, cert_type: str) -> str:
        """
        Genera un número único de certificado
        Formato: CERT-TYPE-YYYY-NNNN
        """
        year = datetime.now().year
        type_code = cert_type[:3].upper()

        # Contar certificados del tipo y año actual usando text()
        sql_query = text("""
            SELECT COUNT(*) FROM certificates 
            WHERE certificate_type = :cert_type
            AND EXTRACT(YEAR FROM created_at) = :year
        """)

        result = self.db.execute(sql_query, {"cert_type": cert_type, "year": year})
        count = result.scalar()

        sequential = (count or 0) + 1
        cert_number = f"CERT-{type_code}-{year}-{sequential:04d}"

        # Verificar unicidad usando text()
        check_query = text("""
            SELECT COUNT(*) FROM certificates 
            WHERE certificate_number = :cert_number
        """)

        result = self.db.execute(check_query, {"cert_number": cert_number})
        exists = result.scalar()

        while exists > 0:
            sequential += 1
            cert_number = f"CERT-{type_code}-{year}-{sequential:04d}"
            result = self.db.execute(check_query, {"cert_number": cert_number})
            exists = result.scalar()

        return cert_number