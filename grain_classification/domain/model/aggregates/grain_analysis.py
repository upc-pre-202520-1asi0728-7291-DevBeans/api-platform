from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from shared.domain.aggregate_root import AuditableAbstractAggregateRoot


class GrainAnalysis(AuditableAbstractAggregateRoot):
    """
    Entidad que representa el análisis individual de un grano de café.
    Hereda 'id', 'created_at', 'updated_at'.
    """
    __tablename__ = "grain_analyses"

    # Clave foránea al agregado raíz
    session_id = Column(Integer, ForeignKey("classification_sessions.id"), nullable=False)

    # Almacena la predicción de 4 clases de color (JSONB)
    color_percentages = Column(JSON, nullable=True)

    # Almacena las características de CV (forma, etc.) (JSONB)
    features = Column(JSON, nullable=True)

    # Almacena el resultado final (JSONB)
    quality_assessment = Column(JSON, nullable=True)

    final_score = Column(Float, nullable=True)
    final_category = Column(String, nullable=True)

    # Relación Many-to-One
    session = relationship("ClassificationSession", back_populates="analyses")