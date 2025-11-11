from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import CoffeeLotRepository


class LotNumberGeneratorService:
    """
    Servicio para generar números únicos de lote
    Patrón: LOT-YYYY-NNNN donde YYYY es año y NNNN es secuencial
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = CoffeeLotRepository(db)

    def generate_lot_number(self) -> str:
        """
        Genera un número único de lote para un productor
        Formato: LOT-YYYY-NNNN
        """
        current_year = datetime.now().year

        # --- 2. CORRECCIÓN: ENVOLVER LA CONSULTA EN text() ---
        # Usamos :year como un "parámetro vinculado" (parameter binding)
        # para evitar la inyección SQL, en lugar de un f-string.
        sql_query = text(
            """
            SELECT COUNT(*) FROM coffee_lots 
            WHERE EXTRACT(YEAR FROM created_at) = :year
            """
        )

        # --- 3. EJECUTAR LA CONSULTA PASANDO LOS PARÁMETROS ---
        result = self.db.execute(sql_query, {"year": current_year})
        lots_this_year = result.scalar()

        # Incrementar el secuencial (tu lógica original)
        sequential = (lots_this_year or 0) + 1

        # Formato: LOT-2024-0001
        lot_number = f"LOT-{current_year}-{sequential:04d}"

        # Verificar unicidad (tu lógica original)
        while self.repository.exists_by_lot_number(lot_number):
            sequential += 1
            lot_number = f"LOT-{current_year}-{sequential:04d}"

        return lot_number