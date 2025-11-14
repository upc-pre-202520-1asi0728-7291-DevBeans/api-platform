from sqlalchemy.orm import Session
import shortuuid  # Para generar IDs de sesión amigables (requiere: pip install shortuuid)

from grain_classification.domain.model.aggregates.classification_session import ClassificationSession


class ClassificationSessionRepository:
    """
    Repositorio para manejar la persistencia del Agregado ClassificationSession.
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _generate_session_id() -> str:
        """Genera un ID único para la sesión (SESS-...)"""
        return f"SESS-{shortuuid.uuid()[:12].upper()}"

    def get_by_id(self, session_id: int) -> ClassificationSession | None:
        return self.db.query(ClassificationSession).filter(ClassificationSession.id == session_id).first()

    def get_by_lot_id(self, lot_id: int) -> list[ClassificationSession]:
        return self.db.query(ClassificationSession).filter(ClassificationSession.coffee_lot_id == lot_id).order_by(
            ClassificationSession.created_at.desc()).all()

    def add(self, session: ClassificationSession):
        """Añade una nueva sesión y sus análisis de granos a la BD."""
        session.session_id_vo = self._generate_session_id()
        self.db.add(session)

    def commit(self):
        """Confirma la transacción."""
        self.db.commit()

    def refresh(self, session: ClassificationSession):
        """Refresca el objeto con los datos de la BD (ej. para obtener el ID)."""
        self.db.refresh(session)