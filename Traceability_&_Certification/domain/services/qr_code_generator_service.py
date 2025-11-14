import qrcode
from io import BytesIO
import base64
import json
from typing import Dict, Any, Optional


class QRCodeGeneratorService:
    """
    Servicio para generar códigos QR para trazabilidad
    """

    def __init__(self):
        self.base_url = "https://api.beandetect.com/traceability"

    def generate_qr_for_record(self, record_number: str, additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Genera un código QR para un registro de trazabilidad
        Retorna el QR como base64 en formato data URI
        """
        # Crear URL de verificación
        verification_url = f"{self.base_url}/verify/{record_number}"

        # Datos adicionales opcionales
        qr_data = {
            "url": verification_url,
            "record_number": record_number,
            "type": "traceability"
        }

        if additional_data:
            qr_data.update(additional_data)

        # Generar QR
        return self._generate_qr_code(json.dumps(qr_data))

    def generate_qr_for_certificate(self, certificate_number: str, certificate_type: str) -> str:
        """
        Genera un código QR para un certificado
        Retorna el QR como base64 en formato data URI
        """
        verification_url = f"{self.base_url}/certificate/{certificate_number}"

        qr_data = {
            "url": verification_url,
            "certificate_number": certificate_number,
            "certificate_type": certificate_type,
            "type": "certificate"
        }

        return self._generate_qr_code(json.dumps(qr_data))

    def generate_qr_for_lot(self, lot_number: str, producer_name: str) -> str:
        """
        Genera un código QR para consultar información completa de un lote
        """
        verification_url = f"{self.base_url}/lot/{lot_number}"

        qr_data = {
            "url": verification_url,
            "lot_number": lot_number,
            "producer": producer_name,
            "type": "lot_info"
        }

        return self._generate_qr_code(json.dumps(qr_data))

    def _generate_qr_code(self, data: str) -> str:
        """
        Genera el código QR y lo retorna como string base64 en formato data URI
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()

        return f"data:image/png;base64,{img_base64}"

    def save_qr_to_file(self, data: str, filename: str) -> str:
        """
        Genera y guarda un código QR como archivo
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)

        return filename