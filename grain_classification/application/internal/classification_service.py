import time
import cv2
from sqlalchemy.orm import Session

from grain_classification.domain.model.aggregates.classification_session import ClassificationSession
from grain_classification.domain.model.aggregates.grain_analysis import GrainAnalysis
from grain_classification.domain.model.valueobjetcs.quality_models import CNN_CLASS_TO_SCORE_MAP
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from grain_classification.infrastructure.persistence.database.repositories.classification_session_repository import \
    ClassificationSessionRepository


# Infraestructura
# Dominio


class ClassificationApplicationService:
    """
    Servicio de aplicación que orquesta el caso de uso de clasificación
    con persistencia en la base de datos.
    """

    def __init__(self, db: Session, cv_service: CVService, ml_predictor: MLPredictorService,
                 grading_service: QualityGradingService):
        self.db = db
        self.repo = ClassificationSessionRepository(db)
        self.cv_service = cv_service
        self.ml_predictor = ml_predictor
        self.grading_service = grading_service

    def start_classification_session(self, coffee_lot_id: int, image_bytes: bytes,
                                     user_id: int) -> ClassificationSession:

        start_time = time.time()

        # 1. Crear el Agregado Raíz (en memoria)
        session = ClassificationSession(coffee_lot_id=coffee_lot_id, user_id=user_id)

        try:
            # 2. Cargar y segmentar (Infraestructura CV)
            original_image = self.cv_service.load_image_from_bytes(image_bytes)
            if original_image is None: raise ValueError("No se pudo cargar la imagen")

            beans_data = self.cv_service.segment_beans(original_image)
            if not beans_data: raise ValueError("No se detectaron granos en la imagen")

            bean_assessments_for_report = []

            # 3. Bucle de análisis de granos
            for bean_data in beans_data:
                bean_image = bean_data['image']
                contour = bean_data['contour']

                features = self.cv_service.extract_all_features(bean_image, contour)

                rgb_image_for_model = cv2.cvtColor(bean_image, cv2.COLOR_BGR2RGB)
                model_input = cv2.resize(rgb_image_for_model, (224, 224))

                # 4. Predecir (Infraestructura IA)
                color_percentages = self.ml_predictor.predict_color_percentages(model_input)
                if color_percentages is None:
                    raise Exception("Modelo CNN no disponible o falló la predicción.")

                # 5. Obtener puntuación base (Dominio)
                winning_class = max(color_percentages, key=color_percentages.get)
                base_score = CNN_CLASS_TO_SCORE_MAP.get(winning_class, 0.0)

                # 6. Obtener puntuación final (Dominio)
                quality_result = self.grading_service.calculate_final_quality(
                    base_score, winning_class, features
                )

                # 7. Crear la Entidad y añadirla a la sesión
                analysis = GrainAnalysis(
                    features=features,
                    color_percentages=color_percentages,
                    quality_assessment=quality_result,
                    final_score=quality_result.get('final_score'),
                    final_category=quality_result.get('quality_category')
                )
                session.analyses.append(analysis)  # SQLAlchemy maneja la relación
                bean_assessments_for_report.append(quality_result)

            # 8. Generar reporte de lote (Dominio)
            batch_report = self.grading_service.generate_batch_report(bean_assessments_for_report)

            # 9. Finalizar la sesión (Agregado)
            time_taken = time.time() - start_time
            session.complete(batch_report, time_taken)

        except Exception as e:
            session.fail(str(e))

        # 10. Persistir el Agregado (Repositorio)
        self.repo.add(session)
        self.repo.commit()
        self.repo.refresh(session)

        return session