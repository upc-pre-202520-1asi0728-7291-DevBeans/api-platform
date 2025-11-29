# traceability_certification/domain/services/hash_service.py

import hashlib
import json
from typing import Dict, Any


class HashService:
    """
    Servicio de dominio para generar hashes inmutables criptográficos.

    Responsabilidad: Crear identificadores únicos e inmutables para
    certificaciones de calidad de granos de café.
    """

    @staticmethod
    def generate_certification_hash(classification_data: Dict[str, Any]) -> str:
        """
        Genera un hash SHA-256 inmutable basado en los datos de clasificación.

        Args:
            classification_data: Diccionario con datos de la clasificación

        Returns:
            str: Hash SHA-256 en formato hexadecimal (64 caracteres)
        """
        # Extraer datos críticos para el hash
        hash_input = {
            'session_id': classification_data.get('session_id'),
            'coffee_lot_id': classification_data.get('coffee_lot_id'),
            'final_score': classification_data.get('final_score'),
            'final_category': classification_data.get('final_category'),
            'total_grains_analyzed': classification_data.get('total_grains_analyzed'),
            'timestamp': classification_data.get('timestamp'),
            'processing_time': classification_data.get('processing_time_seconds')
        }

        # Convertir a JSON ordenado para consistencia
        json_string = json.dumps(hash_input, sort_keys=True, separators=(',', ':'))

        # Generar hash SHA-256
        hash_object = hashlib.sha256(json_string.encode('utf-8'))
        return hash_object.hexdigest()

    @staticmethod
    def verify_hash(original_data: Dict[str, Any], provided_hash: str) -> bool:
        """
        Verifica si un hash coincide con los datos originales.

        Args:
            original_data: Datos originales de la clasificación
            provided_hash: Hash proporcionado para verificar

        Returns:
            bool: True si el hash es válido, False si no coincide
        """
        recalculated_hash = HashService.generate_certification_hash(original_data)
        return recalculated_hash == provided_hash

    @staticmethod
    def generate_verification_token() -> str:
        """
        Genera un token único para verificación pública (QR codes).

        Returns:
            str: Token único de 12 caracteres
        """
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))

    @staticmethod
    def hash_grain_data(grain_analysis: Dict[str, Any]) -> str:
        """
        Genera hash específico para un análisis individual de grano.

        Args:
            grain_analysis: Datos del análisis del grano

        Returns:
            str: Hash SHA-256 del grano individual
        """
        grain_input = {
            'grain_id': grain_analysis.get('id'),
            'color_percentages': grain_analysis.get('color_percentages'),
            'final_score': grain_analysis.get('final_score'),
            'final_category': grain_analysis.get('final_category'),
            'features': grain_analysis.get('features')
        }

        json_string = json.dumps(grain_input, sort_keys=True, separators=(',', ':'))
        hash_object = hashlib.sha256(json_string.encode('utf-8'))
        return hash_object.hexdigest()