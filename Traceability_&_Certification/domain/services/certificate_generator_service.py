from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from io import BytesIO
import hashlib
import json
from typing import Dict, Any, Optional
import base64


class CertificateGeneratorService:
    """
    Servicio para generar certificados digitales en formato PDF
    """

    def __init__(self):
        self.page_width, self.page_height = A4

    def generate_certificate_pdf(
            self,
            certificate_data: Dict[str, Any],
            qr_code_base64: Optional[str] = None
    ) -> BytesIO:
        """
        Genera un certificado PDF profesional
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Fondo y bordes decorativos
        self._draw_border(c, width, height)

        # Header con logo (espacio para logo)
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor("#2c5530"))
        c.drawCentredString(width/2, height - 80, "CERTIFICADO DE TRAZABILIDAD")

        # Línea decorativa
        c.setStrokeColor(colors.HexColor("#8b4513"))
        c.setLineWidth(2)
        c.line(100, height - 100, width - 100, height - 100)

        # Número de certificado
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(100, height - 120, f"Certificado N°: {certificate_data.get('certificate_number', 'N/A')}")
        c.drawRightString(width - 100, height - 120, f"Fecha de emisión: {certificate_data.get('issue_date', 'N/A')}")

        # Información principal
        y_position = height - 160
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "INFORMACIÓN DEL LOTE")

        y_position -= 30
        c.setFont("Helvetica", 11)

        # Tabla con información del lote
        data_table = [
            ["Número de Lote:", certificate_data.get('lot_number', 'N/A')],
            ["Productor:", certificate_data.get('producer_name', 'N/A')],
            ["Variedad de Café:", certificate_data.get('coffee_variety', 'N/A')],
            ["Origen:", certificate_data.get('origin', 'N/A')],
            ["Altitud:", f"{certificate_data.get('altitude', 'N/A')} msnm"],
            ["Cantidad:", f"{certificate_data.get('quantity', 'N/A')} kg"],
            ["Método de Procesamiento:", certificate_data.get('processing_method', 'N/A')],
        ]

        for label, value in data_table:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_position, label)
            c.setFont("Helvetica", 10)
            c.drawString(250, y_position, str(value))
            y_position -= 25

        # Tipo de certificación
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "CERTIFICACIÓN")

        y_position -= 30
        c.setFont("Helvetica", 11)
        cert_type = certificate_data.get('certificate_type', 'QUALITY')
        c.drawString(100, y_position, f"Tipo: {cert_type}")

        y_position -= 25
        if certificate_data.get('description'):
            c.setFont("Helvetica", 9)
            description = certificate_data['description']
            # Dividir descripción en líneas si es muy larga
            if len(description) > 80:
                lines = [description[i:i+80] for i in range(0, len(description), 80)]
                for line in lines[:3]:  # Máximo 3 líneas
                    c.drawString(100, y_position, line)
                    y_position -= 15
            else:
                c.drawString(100, y_position, description)
                y_position -= 25

        # Autoridad emisora
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, "Emitido por:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        c.drawString(100, y_position, certificate_data.get('issuing_authority', 'N/A'))

        # QR Code
        if qr_code_base64:
            try:
                # Remover el prefijo data:image/png;base64, si existe
                if qr_code_base64.startswith('data:image'):
                    qr_code_base64 = qr_code_base64.split(',')[1]

                qr_image_data = base64.b64decode(qr_code_base64)
                qr_buffer = BytesIO(qr_image_data)

                # Dibujar QR en la esquina inferior derecha
                c.drawImage(
                    ImageReader(qr_buffer),
                    width - 200,
                    80,
                    width=120,
                    height=120
                )

                c.setFont("Helvetica", 8)
                c.drawCentredString(width - 140, 60, "Escanea para verificar")
            except Exception as e:
                print(f"Error al agregar QR: {e}")

        # Hash de verificación
        verification_hash = certificate_data.get('verification_hash', 'N/A')
        c.setFont("Helvetica", 7)
        c.drawString(50, 40, f"Hash de verificación: {verification_hash[:64]}...")

        # Fecha de vencimiento si existe
        if certificate_data.get('expiry_date'):
            c.drawRightString(width - 50, 40, f"Válido hasta: {certificate_data['expiry_date']}")

        # Footer
        c.setFont("Helvetica-Italic", 8)
        c.setFillColor(colors.grey)
        c.drawCentredString(width/2, 20, "Este certificado ha sido generado electrónicamente y registrado en blockchain")

        c.save()
        buffer.seek(0)
        return buffer

    def _draw_border(self, c, width, height):
        """Dibuja un borde decorativo en el certificado"""
        c.setStrokeColor(colors.HexColor("#8b4513"))
        c.setLineWidth(3)
        c.rect(30, 30, width - 60, height - 60)

        c.setLineWidth(1)
        c.rect(35, 35, width - 70, height - 70)

    def calculate_verification_hash(self, certificate_data: Dict[str, Any]) -> str:
        """
        Calcula un hash de verificación para el certificado
        """
        # Datos relevantes para el hash
        hash_data = {
            'certificate_number': certificate_data.get('certificate_number'),
            'lot_number': certificate_data.get('lot_number'),
            'issue_date': str(certificate_data.get('issue_date')),
            'certificate_type': certificate_data.get('certificate_type'),
            'issuing_authority': certificate_data.get('issuing_authority')
        }

        data_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def generate_simple_certificate(
            self,
            certificate_number: str,
            lot_info: Dict[str, Any],
            cert_type: str
    ) -> BytesIO:
        """
        Genera un certificado simple sin todos los detalles
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Título
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height - 100, "CERTIFICADO")

        # Info básica
        y = height - 150
        c.setFont("Helvetica", 12)
        c.drawString(100, y, f"Certificado: {certificate_number}")
        y -= 30
        c.drawString(100, y, f"Tipo: {cert_type}")
        y -= 30
        c.drawString(100, y, f"Lote: {lot_info.get('lot_number', 'N/A')}")

        c.save()
        buffer.seek(0)
        return buffer