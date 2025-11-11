# Categorías de Calidad (Regla de Negocio)
QUALITY_CATEGORIES = ['Specialty', 'Premium', 'A', 'B', 'C']

# Umbrales (Regla de Negocio)
QUALITY_THRESHOLDS = {
    'Specialty': 0.9,
    'Premium': 0.8,
    'A': 0.7,
    'B': 0.6,
    'C': 0.0
}

# Clases del Modelo (Conocimiento del Dominio sobre la IA)
CNN_COLOR_CLASSES = ['Dark', 'Green', 'Light', 'Medium']

# Mapeo de Puntuación (Regla de Negocio)
CNN_CLASS_TO_SCORE_MAP = {
    'Light': 0.95,   # Base para Specialty
    'Medium': 0.85,  # Base para Premium
    'Dark': 0.40,    # Base para C
    'Green': 0.40    # Base para C
}