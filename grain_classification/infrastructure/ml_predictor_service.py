import numpy as np
from tensorflow import keras
import os


class MLPredictorService:
    """
    Implementación de infraestructura para cargar y ejecutar el modelo CNN.
    """

    def __init__(self, model_path: str, color_classes: list[str]):
        self.model_path = model_path
        self.color_classes = color_classes
        self.cnn_model = self._load_model()

    def _load_model(self):
        """
        Carga el modelo CNN real. Si falla, devuelve None.
        """
        if not os.path.exists(self.model_path):
            print(f"ERROR CRÍTICO AL CARGAR MODELO CNN: No se encontró el archivo en {self.model_path}")
            return None

        try:
            # Advertencia de Keras sobre métricas compiladas es normal en la carga
            model = keras.models.load_model(self.model_path)
            print(f"Modelo CNN real cargado exitosamente desde: {self.model_path}")
            return model
        except Exception as e:
            print(f"ERROR CRÍTICO AL CARGAR MODELO CNN: {e}")
            return None

    def predict_color_percentages(self, processed_image: np.ndarray) -> dict | None:
        """
        Predice los porcentajes de confianza para cada clase de color.
        """
        if self.cnn_model is None:
            return None  # El modelo no se cargó

        try:
            normalized_image = processed_image / 255.0
            input_tensor = np.expand_dims(normalized_image, axis=0)
            raw_predictions = self.cnn_model.predict(input_tensor, verbose=0)[0]

            predictions = {}
            for i, color_class in enumerate(self.color_classes):
                predictions[color_class] = round(raw_predictions[i].item(), 3)

            total_prob = sum(predictions.values())
            if total_prob > 0:
                predictions = {k: (v / total_prob) * 100 for k, v in predictions.items()}

            return predictions
        except Exception as e:
            print(f"Error durante la predicción de la CNN: {e}")
            return None