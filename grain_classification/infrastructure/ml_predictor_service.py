import numpy as np
from tensorflow import keras
import os
import requests
import time
from shared.infrastructure.persistence.database.repositories.settings import settings


class MLPredictorService:
    """
    Servicio de predicción con estrategia de carga inteligente:
    1. Intenta cargar desde ruta local primero
    2. Si falla, descarga desde Blob Storage
    """

    def __init__(self, model_path: str, color_classes: list[str]):
        self.model_path = model_path
        self.color_classes = color_classes
        self.cnn_model = self._load_model()

    def _download_model_from_blob(self) -> bool:
        """Descarga el modelo de ml desde Azure Blob Storage."""
        # Usar settings en lugar de os.environ
        model_blob_url = settings.MODEL_BLOB_URL

        # Verificar que no sea el valor por defecto
        if not model_blob_url or model_blob_url == "https://your-blob-storage-url-here":
            print("ERROR: MODEL_BLOB_URL no está configurada correctamente.")
            print("Valor actual:", model_blob_url)
            print("Verifica tu archivo .env o variables de entorno")
            return False

        print(f"Descargando modelo desde Blob Storage...")
        print(f"URL: {model_blob_url.split('?')[0] if '?' in model_blob_url else model_blob_url}")

        try:
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            # Descargar con streaming para archivos grandes
            response = requests.get(model_blob_url, stream=True, timeout=300)
            response.raise_for_status()

            # Guardar el archivo en chunks
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            print(f"Tamaño total: {total_size / (1024 ** 2):.1f} MB")

            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Log progreso cada 50MB
                        if downloaded % (50 * 1024 * 1024) == 0:
                            progress = (downloaded / total_size * 100) if total_size > 0 else 0
                            print(
                                f"  Progreso: {downloaded / (1024 ** 2):.1f} MB / {total_size / (1024 ** 2):.1f} MB ({progress:.1f}%)")

            print(f"✅ Descarga completada: {downloaded / (1024 ** 2):.1f} MB")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR DE RED al descargar desde Blob Storage: {e}")
            return False
        except Exception as e:
            print(f"❌ ERROR al guardar modelo descargado: {e}")
            return False

    def _load_model(self):
        """
        Carga el modelo CNN con estrategia de fallback:
        1. Intenta cargar desde ruta local primero (rápido)
        2. Si falla, descarga desde Blob Storage (lento)
        3. Intenta cargar después de descarga
        """
        # ESTRATEGIA 1: Intentar carga local primero (lo más común)
        if os.path.exists(self.model_path):
            try:
                print(f"📂 Cargando modelo desde: {self.model_path}")
                model = keras.models.load_model(self.model_path)
                file_size = os.path.getsize(self.model_path) / (1024 ** 2)
                print(f"Modelo CNN cargado desde disco ({file_size:.1f} MB)")
                return model
            except Exception as e:
                print(f"Falló carga local del modelo: {e}")
                print("Intentando descarga desde Blob Storage...")
                # Eliminar archivo corrupto
                try:
                    os.remove(self.model_path)
                    print("Archivo corrupto eliminado")
                except Exception as remove_error:
                    print(f"No se pudo eliminar archivo corrupto: {remove_error}")

        # ESTRATEGIA 2: Descargar desde Blob Storage (solo si no existe localmente)
        print(f"📥 Modelo no encontrado localmente. Descargando desde Blob Storage...")

        if not self._download_model_from_blob():
            print("❌ CRÍTICO: No se pudo descargar el modelo desde Blob Storage")
            print(f"   Ruta esperada: {self.model_path}")
            print(f"   Configuración actual: MODEL_BLOB_URL = {settings.MODEL_BLOB_URL[:50]}...")
            return None

        # Esperar un momento para asegurar que el archivo esté completamente escrito
        time.sleep(1)

        # ESTRATEGIA 3: Intentar carga después de descarga
        try:
            print(f"📂 Cargando modelo descargado...")
            model = keras.models.load_model(self.model_path)
            file_size = os.path.getsize(self.model_path) / (1024 ** 2)
            print(f"✅ Modelo CNN cargado exitosamente después de descarga ({file_size:.1f} MB)")
            return model
        except Exception as e:
            print(f"❌ CRÍTICO: Error al cargar modelo después de descarga: {e}")
            return None

    def predict_color_percentages(self, processed_image: np.ndarray) -> dict | None:
        """
        Predice los porcentajes de confianza para cada clase de color.
        """
        if self.cnn_model is None:
            print("❌ Modelo no disponible para predicción")
            return None

        try:
            # Normalizar imagen
            normalized_image = processed_image / 255.0
            input_tensor = np.expand_dims(normalized_image, axis=0)

            # Predicción
            raw_predictions = self.cnn_model.predict(input_tensor, verbose=0)[0]

            # Convertir a diccionario
            predictions = {}
            for i, color_class in enumerate(self.color_classes):
                predictions[color_class] = round(raw_predictions[i].item(), 3)

            # Normalizar a 100%
            total_prob = sum(predictions.values())
            if total_prob > 0:
                predictions = {k: (v / total_prob) * 100 for k, v in predictions.items()}

            return predictions

        except Exception as e:
            print(f"❌ Error durante predicción CNN: {e}")
            return None