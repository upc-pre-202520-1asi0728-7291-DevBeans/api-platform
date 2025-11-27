import time
import cv2
from sqlalchemy.orm import Session
from typing import Optional

from grain_classification.domain.model.aggregates.classification_session import ClassificationSession
from grain_classification.domain.model.aggregates.grain_analysis import GrainAnalysis
from grain_classification.domain.model.valueobjetcs.quality_models import CNN_CLASS_TO_SCORE_MAP
from grain_classification.domain.services.grading_service import QualityGradingService
from grain_classification.infrastructure.cv_service import CVService
from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
from grain_classification.infrastructure.cloudinary_service import CloudinaryService
from grain_classification.infrastructure.persistence.database.repositories.classification_session_repository import \
    ClassificationSessionRepository
from shared.infrastructure.notification_service import email_service


class ClassificationApplicationService:
    """
    Servicio de aplicación que orquesta el caso de uso de clasificación
    con persistencia en la base de datos y almacenamiento de imágenes.
    """

    def __init__(self, db: Session, cv_service: CVService, ml_predictor: MLPredictorService,
                 grading_service: QualityGradingService, cloudinary_service: CloudinaryService):
        self.db = db
        self.repo = ClassificationSessionRepository(db)
        self.cv_service = cv_service
        self.ml_predictor = ml_predictor
        self.grading_service = grading_service
        self.cloudinary_service = cloudinary_service

    def start_classification_session(self, coffee_lot_id: int, image_bytes: bytes,
                                     user_id: int, user_email: Optional[str] = None,
                                     send_email_notification: bool = False) -> ClassificationSession:

        start_time = time.time()

        # 1. Crear el Agregado Raíz (en memoria)
        session = ClassificationSession(coffee_lot_id=coffee_lot_id, user_id=user_id)

        try:
            # 2. Cargar y segmentar (Infraestructura CV)
            original_image = self.cv_service.load_image_from_bytes(image_bytes)
            if original_image is None:
                raise ValueError("No se pudo cargar la imagen")

            beans_data = self.cv_service.segment_beans(original_image)
            if not beans_data:
                raise ValueError("No se detectaron granos en la imagen")

            bean_assessments_for_report = []

            # 3. Bucle de análisis de granos
            for idx, bean_data in enumerate(beans_data):
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

                # 7. Subir imagen a Cloudinary (NUEVO)
                # Nota: session.id aún no existe, usaremos un ID temporal
                session_id_temp = f"temp_{int(time.time())}_{coffee_lot_id}"
                upload_result = self.cloudinary_service.upload_grain_image(
                    bean_image,
                    session_id_temp,
                    idx
                )

                # 8. Crear la Entidad y añadirla a la sesión
                analysis = GrainAnalysis(
                    features=features,
                    color_percentages=color_percentages,
                    quality_assessment=quality_result,
                    final_score=quality_result.get('final_score'),
                    final_category=quality_result.get('quality_category'),
                    image_url=upload_result.get('url'),
                    cloudinary_public_id=upload_result.get('public_id')
                )
                session.analyses.append(analysis)
                bean_assessments_for_report.append(quality_result)

            # 9. Generar reporte de lote (Dominio)
            batch_report = self.grading_service.generate_batch_report(bean_assessments_for_report)

            # 10. Finalizar la sesión (Agregado)
            time_taken = time.time() - start_time
            session.complete(batch_report, time_taken)

        except Exception as e:
            session.fail(str(e))

        # 11. Persistir el Agregado (Repositorio)
        self.repo.add(session)
        self.repo.commit()
        self.repo.refresh(session)

        # 12. Enviar notificación por email si está habilitada y hay email
        if send_email_notification and user_email and session.status == "COMPLETED":
            try:
                # Obtener datos del lote de café (opcional)
                from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import \
                    CoffeeLotRepository
                lot_repo = CoffeeLotRepository(self.db)
                coffee_lot = lot_repo.find_by_id(coffee_lot_id)
                
                coffee_lot_data = {
                    'lot_number': coffee_lot.lot_number if coffee_lot else 'N/A'
                }

                # Si es un solo grano, agregar sus datos específicos
                if session.total_grains_analyzed == 1 and session.analyses:
                    grain = session.analyses[0]
                    coffee_lot_data['grain_id'] = grain.id
                    coffee_lot_data['final_score'] = (grain.final_score * 100) if grain.final_score else 0
                    coffee_lot_data['final_category'] = grain.final_category or 'N/A'

                # Convertir sesión a dict para el servicio de email
                session_dict = {
                    'session_id_vo': session.session_id_vo,
                    'classification_result': session.classification_result,
                    'processing_time_seconds': session.processing_time_seconds,
                    'completed_at': session.completed_at
                }

                email_service.send_classification_report(
                    recipient_email=user_email,
                    classification_data=session_dict,
                    coffee_lot_data=coffee_lot_data
                )
                print(f"Notificación enviada a {user_email}")
            except Exception as e:
                print(f"Error al enviar notificación por email: {e}")
                # No fallamos toda la clasificación si falla el envío de email

        return session