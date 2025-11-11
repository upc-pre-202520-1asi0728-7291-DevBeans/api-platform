from grain_classification.domain.model.valueobjetcs.quality_models import QUALITY_THRESHOLDS, QUALITY_CATEGORIES


class QualityGradingService:
    """
    Servicio de dominio para aplicar reglas de negocio de clasificación.
    (Lógica de quality_classifier.py)
    """

    def __init__(self):
        self.quality_thresholds = QUALITY_THRESHOLDS
        self.quality_categories = QUALITY_CATEGORIES

    def calculate_final_quality(self, base_score: float, source_category: str, features: dict) -> dict:
        """
        Combina la puntuación de IA con las características de CV (forma).
        """
        shape_score = self._evaluate_shape_quality(features)

        # Ponderación 70% IA (color) / 30% CV (forma)
        final_score = (base_score * 0.7) + (shape_score * 0.3)
        final_category = self._determine_quality_category(final_score)

        return {
            'quality_category': final_category,
            'final_score': round(final_score, 3),
            'base_quality_score': base_score,
            'shape_score': shape_score,
            'source_category (color)': source_category
        }

    @staticmethod
    def _evaluate_shape_quality(features: dict) -> float:
        """Evalúa la calidad de la forma."""
        shape_score = 1.0
        circularity = features.get('circularity', 0.5)
        if circularity < 0.7:
            shape_score -= 0.3
        if features.get('has_cracks', False):
            shape_score -= 0.2
        return max(0.0, shape_score)

    def _determine_quality_category(self, final_score: float) -> str:
        """Asigna la categoría de negocio final."""
        for category, threshold in self.quality_thresholds.items():
            if final_score >= threshold:
                return category
        return 'C'

    def generate_batch_report(self, bean_assessments: list[dict]) -> dict:
        """Genera el reporte consolidado para el lote (Sesión de Clasificación)."""
        total_beans = len(bean_assessments)
        if total_beans == 0:
            return {"error": "No se analizaron granos"}

        category_count = {category: 0 for category in self.quality_categories}
        for bean in bean_assessments:
            category = bean['quality_category']
            if category in category_count:
                category_count[category] += 1

        avg_score = sum(bean['final_score'] for bean in bean_assessments) / total_beans
        lot_quality = self._determine_quality_category(avg_score)

        return {
            'total_beans_analyzed': total_beans,
            'category_distribution': category_count,
            'average_quality_score': round(avg_score, 3),
            'lot_quality': lot_quality
        }