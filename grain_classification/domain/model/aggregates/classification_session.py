import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from shared.domain.aggregate_root import AuditableAbstractAggregateRoot


class SessionStatus(str, enum.Enum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ClassificationSession(AuditableAbstractAggregateRoot):
    """
    Agregado Raíz (Aggregate Root) que representa una sesión de clasificación.
    Hereda 'id', 'created_at', 'updated_at' de AuditableAbstractAggregateRoot.
    """
    __tablename__ = "classification_sessions"

    # Identificador legible (SESS-YYYYMMDD-...)
    session_id_vo = Column(String, unique=True, index=True)

    # Claves foráneas a otros Bounded Contexts
    coffee_lot_id = Column(Integer, ForeignKey("coffee_lots.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(SessionStatus), default=SessionStatus.STARTED)

    total_grains_analyzed = Column(Integer, default=0)
    processing_time_seconds = Column(Float, nullable=True)

    # Almacena el reporte final (JSONB en PostgreSQL)
    classification_result = Column(JSON, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relación One-to-Many: Una sesión tiene muchos análisis de granos
    analyses = relationship("GrainAnalysis", back_populates="session", cascade="all, delete-orphan")

    def complete(self, report: dict, time_taken: float):
        """Finaliza la sesión, actualiza estado y resultados."""
        self.status = SessionStatus.COMPLETED
        self.classification_result = report
        self.total_grains_analyzed = report.get('total_beans_analyzed', 0)
        self.processing_time_seconds = time_taken
        self.completed_at = datetime.now(UTC)

    def fail(self, reason: str):
        self.status = SessionStatus.FAILED
        self.classification_result = {"error": reason}
        self.completed_at = datetime.now(UTC)