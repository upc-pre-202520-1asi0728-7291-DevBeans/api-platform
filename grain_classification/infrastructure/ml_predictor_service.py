import numpy as np
from tensorflow import keras
import os
import requests  # Used for downloading the model from the public URL
import time

# This URL will be set via an Azure App Setting/Environment Variable
MODEL_BLOB_URL = os.environ.get("MODEL_BLOB_URL")


class MLPredictorService:
    """
    Implementación de infraestructura para cargar y ejecutar el modelo CNN.
    """

    def __init__(self, model_path: str, color_classes: list[str]):
        self.model_path = model_path
        self.color_classes = color_classes
        self.cnn_model = self._load_model()

    def _download_model(self) -> bool:
        """Downloads the .h5 model from the Azure Blob URL."""
        if not MODEL_BLOB_URL:
            print("ERROR: MODEL_BLOB_URL no está configurada en las App Settings de Azure.")
            return False

        print(f"Modelo no encontrado. Iniciando descarga desde Blob Storage: {MODEL_BLOB_URL}")

        try:
            # Create the directory structure (e.g., 'ml_models/')
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            # Use requests to download the large file in chunks
            response = requests.get(MODEL_BLOB_URL, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # Save the content to the local path
            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("Descarga del modelo exitosa.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"ERROR DE RED/DESCARGA (Blob Storage): {e}")
            return False
        except Exception as e:
            print(f"ERROR al guardar el modelo descargado: {e}")
            return False

    def _load_model(self):
        """
        Carga el modelo CNN real. Si no existe, intenta descargarlo.
        """
        # 1. Check if the file exists locally
        if not os.path.exists(self.model_path):
            # 2. If missing, attempt to download it
            if not self._download_model():
                # If download fails, fail the load process
                return None
            # Wait briefly to ensure file handle is released after writing (optional, but safer)
            time.sleep(1)

            # 3. Load the model from the local path
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
        (This function remains the same as its prediction logic is sound)
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