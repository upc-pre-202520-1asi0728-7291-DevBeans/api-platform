# shared/infrastructure/notification_service.py

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


def _generate_report_html(
        classification_data: Dict[str, Any],
        coffee_lot_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Genera el contenido HTML del reporte de clasificación.
    """
    result = classification_data.get('classification_result', {})
    session_id = classification_data.get('session_id_vo', 'N/A')
    total_beans = result.get('total_beans_analyzed', 0)
    processing_time = classification_data.get('processing_time_seconds', 0)

    # Obtener distribución de calidad
    quality_dist = result.get('quality_distribution', {})
    avg_score = result.get('average_quality_score', 0) * 100

    # Verificar si es un análisis de grano individual
    is_single_grain = total_beans == 1

    # Nombre del lote
    lot_name = coffee_lot_data.get('lot_number', 'N/A') if coffee_lot_data else 'N/A'

    # En caso sea un solo grano, obtener sus datos específicos
    single_grain_id = coffee_lot_data.get('grain_id', 'N/A') if is_single_grain and coffee_lot_data else 'N/A'
    single_grain_score = coffee_lot_data.get('final_score', 0) if is_single_grain and coffee_lot_data else avg_score
    single_grain_category = coffee_lot_data.get('final_category',
                                                'N/A') if is_single_grain and coffee_lot_data else 'N/A'

    # Fecha de la clasificación
    completed_at = classification_data.get('completed_at', datetime.now())
    if isinstance(completed_at, str):
        fecha_str = completed_at.split('T')[0]
    else:
        fecha_str = completed_at.strftime('%Y-%m-%d')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .info-card {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .info-label {{
                font-weight: bold;
                color: #555;
            }}
            .info-value {{
                color: #333;
            }}
            .quality-section {{
                margin: 30px 0;
            }}
            .quality-bar {{
                background: #e0e0e0;
                border-radius: 10px;
                height: 30px;
                overflow: hidden;
                margin: 10px 0;
            }}
            .quality-fill {{
                background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }}
            .distribution-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .distribution-table th,
            .distribution-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .distribution-table th {{
                background-color: #667eea;
                color: white;
            }}
            .distribution-table tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e0e0e0;
                text-align: center;
                color: #777;
                font-size: 14px;
            }}
            .metric {{
                display: inline-block;
                background: white;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 15px 25px;
                margin: 10px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Reporte de Clasificación de Café</h1>
            <p>Sesión: {session_id}</p>
        </div>

        <div class="info-card">
            <div class="info-row">
                <span class="info-label">Lote de Café:</span>
                <span class="info-value">{lot_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Fecha de Clasificación:</span>
                <span class="info-value">{fecha_str}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Tiempo de Procesamiento:</span>
                <span class="info-value">{processing_time:.2f} segundos</span>
            </div>
        </div>

        <div class="quality-section">
            <h2>Resultados de Análisis</h2>

            <div style="text-align: center; margin: 30px 0;">"""

    # Mostrar métricas según si es un solo grano o múltiples
    if is_single_grain:
        html += f"""
                <div class="metric">
                    <div class="metric-value">#{single_grain_id}</div>
                    <div class="metric-label">Grano Analizado</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{single_grain_score:.1f}%</div>
                    <div class="metric-label">Puntaje Obtenido</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{single_grain_category}</div>
                    <div class="metric-label">Categoría Final</div>
                </div>"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>BeanDetect AI</strong> - Sistema de Clasificación Inteligente de Café</p>
            <p>Este reporte fue generado automáticamente por el sistema.</p>
        </div>
    </body>
    </html>
    """

    return html


class EmailNotificationService:
    """
    Servicio para envío de notificaciones por correo electrónico usando SMTP.
    No requiere servicios de pago - usa configuración SMTP del usuario.
    """

    def __init__(self):
        # Configuración SMTP desde variables de entorno
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SMTP_SENDER_EMAIL", self.smtp_username)
        self.enabled = bool(self.smtp_username and self.smtp_password)

    def send_classification_report(
            self,
            recipient_email: str,
            classification_data: Dict[str, Any],
            coffee_lot_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía un reporte de clasificación por correo electrónico.

        Args:
            recipient_email: Email del destinatario
            classification_data: Datos de la clasificación (sesión)
            coffee_lot_data: Datos opcionales del lote de café y grano individual

        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        if not self.enabled:
            print("Servicio de email no configurado. Configure SMTP_USERNAME y SMTP_PASSWORD.")
            return False

        try:
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Reporte de Clasificación - {classification_data.get('session_id_vo', 'N/A')}"
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # Generar contenido HTML del reporte
            html_content = _generate_report_html(classification_data, coffee_lot_data)

            # Adjuntar contenido HTML
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            print(f"Email enviado exitosamente a {recipient_email}")
            return True

        except Exception as e:
            print(f"Error al enviar email: {e}")
            return False


# Singleton global
email_service = EmailNotificationService()