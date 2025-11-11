import cv2
import numpy as np


class CVService:
    """
    Servicio de infraestructura para procesamiento de imágenes (CV) y
    extracción de características.
    """

    def __init__(self, image_size=(224, 224), contrast=1.5, brightness=10):
        self.image_size = image_size
        self.contrast_factor = contrast
        self.brightness_delta = brightness

    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray | None:
        """Carga una imagen desde bytes (ej. de un UploadFile de FastAPI)."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("No se pudieron decodificar los bytes de la imagen")
            return img
        except Exception as e:
            print(f"Error al cargar imagen desde bytes: {e}")
            return None

    @staticmethod
    def segment_beans(image: np.ndarray) -> list[dict]:
        """
        Segmenta granos individuales en la imagen.
        (Lógica de image_processor.py)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Umbralización para separar granos del fondo
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Limpieza morfológica
        kernel = np.ones((5, 5), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        beans_data = []
        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:  # Filtrar ruido
                x, y, w, h = cv2.boundingRect(c)
                bean_image = image[y:y + h, x:x + w]
                beans_data.append({'image': bean_image, 'contour': c})
        return beans_data

    @staticmethod
    def extract_all_features(image: np.ndarray, contour: np.ndarray) -> dict:
        """
        Extrae características de forma y detecta 'grietas'.
        (Lógica de feature_extractor.py)
        """
        features = {}

        # Características de Forma
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0

        features['area'] = area
        features['perimeter'] = perimeter
        features['circularity'] = circularity

        # Detección de 'Grietas' (basada en densidad de bordes)
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_density = np.sum(edges) / (255 * edges.size) if edges.size > 0 else 0

        # Umbral simple: si más del 5% son bordes, asumimos grietas
        has_cracks_bool = edge_density > 0.05
        features['has_cracks'] = str(has_cracks_bool)

        return features