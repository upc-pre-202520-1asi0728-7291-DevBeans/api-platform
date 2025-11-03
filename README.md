# BeanDetect AI - Backend API

Backend desarrollado con FastAPI, Python y PostgreSQL (Supabase) siguiendo los patrones **CQRS** (Command Query Responsibility Segregation) y **DDD** (Domain-Driven Design).

## 🏗️ Arquitectura

El proyecto sigue una arquitectura hexagonal (puertos y adaptadores) con la siguiente estructura:

```
BeanDetectAI/
├── shared/                 # Código compartido y configuración global entre bounded contexts
├── iam_profile/            # Bounded Context: IAM & Profile
├── coffee_lot_management/  # Bounded Context: Coffee Lot Management
├── grain_classification/   # Bounded Context: Grain Classification (TODO)
├── traceability_certification/ # Bounded Context: Traceability & Certification (TODO)
└── reporting_analytics/    # Bounded Context: Reporting & Analytics (TODO)
```

Cada Bounded Context sigue la estructura DDD:
- **domain/**: Lógica de negocio (aggregates, entities, value objects, commands, queries)
- **application/**: Casos de uso (command services, query services)
- **infrastructure/**: Implementaciones técnicas (repositories, persistencia)
- **interfaces/**: Capa de presentación (REST controllers, resources, transformers)

## 🚀 Instalación

### Prerrequisitos

- Python 3.13
- PostgreSQL (Supabase)
- pip

### Pasos de instalación

**Clonar el repositorio**
```bash
git clone <repository-url>
cd BeanDetectAI
```

**Instalar dependencias**
```bash
pip install -r requirements.txt
```

**Inicializar el proyecto**
```bash
# Las tablas se crean automáticamente al iniciar la aplicación
python main.py
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Documentación API

### Bounded Context: IAM & Profile

#### Authentication Endpoints

**POST /api/v1/auth/register/producer**
Registra un nuevo productor independiente.

```json
{
  "email": "juan@email.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "document_number": "12345678",
  "document_type": "DNI",
  "phone_number": "+57 300 123 4567",
  "city": "Chinchiná",
  "country": "Perú",
  "farm_name": "Finca El Cafetal",
  "latitude": 4.9824,
  "longitude": -75.6086,
  "altitude": 1500,
  "region": "Caldas",
  "hectares": 10.5,
  "coffee_varieties": ["CATURRA", "CASTILLO"],
  "production_capacity": 5000
}
```

**POST /api/v1/auth/register/cooperative**
Registra una nueva cooperativa.

```json
{
  "email": "info@cooperativa.com",
  "password": "password123",
  "cooperative_name": "Cooperativa Cafetera del Sur",
  "legal_registration_number": "900.123.456-7",
  "phone_number": "+57 300 123 4567",
  "address": "Calle Principal 123",
  "city": "Manizales",
  "country": "Perú",
  "legal_representative_name": "María García",
  "legal_representative_email": "maria@cooperativa.com",
  "processing_capacity": 100000,
  "certifications": ["ORGANIC", "FAIR_TRADE"]
}
```

**POST /api/v1/auth/login**
Inicia sesión y obtiene token JWT.

```json
{
  "email": "oscargabrielaranda@gmail.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "juan@email.com",
    "user_type": "PRODUCER",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### Profile Endpoints

**GET /api/v1/profiles/{user_id}**
Obtiene el perfil completo de un usuario.

**GET /api/v1/profiles/producer/{producer_id}**
Obtiene el perfil específico de un productor.

**GET /api/v1/profiles/cooperative/{cooperative_id}**
Obtiene el perfil específico de una cooperativa.

### Bounded Context: Coffee Lot Management

**POST /api/v1/coffee-lots**
Registra un nuevo lote de café.

```json
{
  "producer_id": 1,
  "harvest_date": "2024-01-15",
  "coffee_variety": "CATURRA",
  "quantity": 500,
  "processing_method": "WASHED",
  "latitude": 4.9824,
  "longitude": -75.6086,
  "altitude": 1500,
  "soil_type": "Volcanic",
  "climate_zone": "Tropical",
  "farm_section": "Lote A"
}
```

**GET /api/v1/coffee-lots/{lot_id}**
Obtiene información de un lote específico.

**PUT /api/v1/coffee-lots/{lot_id}**
Actualiza información de un lote.

**DELETE /api/v1/coffee-lots/{lot_id}?deletion_reason=motivo**
Elimina un lote (solo si está en estado REGISTERED).

**PATCH /api/v1/coffee-lots/{lot_id}/status**
Cambia el estado de un lote.

```json
{
  "new_status": "PROCESSING",
  "change_reason": "Iniciando procesamiento"
}
```

**GET /api/v1/coffee-lots/producer/{producer_id}**
Obtiene todos los lotes de un productor.

Query parameters:
- `status`: Filtrar por estado (REGISTERED, PROCESSING, CLASSIFIED, etc.)
- `harvest_year`: Filtrar por año de cosecha

**GET /api/v1/coffee-lots/search/advanced**
Búsqueda avanzada de lotes.

Query parameters:
- `variety`: Variedad de café
- `processing_method`: Método de procesamiento
- `min_altitude`: Altitud mínima
- `max_altitude`: Altitud máxima
- `start_date`: Fecha inicio
- `end_date`: Fecha fin
- `status`: Estado del lote


## 🗄️ Base de Datos

La aplicación utiliza PostgreSQL en Supabase con las siguientes características:

- **ORM**: SQLAlchemy
- **Migraciones**: Alembic
- **Connection Pooling**: Configurado para pooler de Supabase

### Tablas principales

#### users
- Usuarios del sistema (productores y cooperativas)
- Autenticación con bcrypt
- Relaciones one-to-one con perfiles

#### producer_profiles
- Información detallada de productores
- Datos de finca y capacidad de producción

#### cooperative_profiles
- Información de cooperativas
- Capacidad de procesamiento y certificaciones

#### coffee_lots
- Lotes de café registrados
- Información de cosecha, variedad, cantidad
- Estados del ciclo de vida

#### origin_data
- Datos detallados de origen geográfico
- Altitud, coordenadas, tipo de suelo


## 🔐 Seguridad

- **Autenticación**: JWT (JSON Web Tokens)
- **Hashing de contraseñas**: bcrypt
- **Validaciones**: Pydantic models
- **CORS**: Configurado para orígenes permitidos


## 📝 Próximos Pasos

Los siguientes Bounded Contexts están pendientes de implementación:

1. **Grain Classification** ✨
   - Sesiones de clasificación con IA
   - Detección de defectos
   - Cálculo de métricas de calidad

2. **Traceability & Certification** 🔗
   - Registro de trazabilidad
   - Generación de QR codes
   - Integración con blockchain
   - Emisión de certificados digitales

3. **Reporting & Analytics** 📈
   - Generación de reportes
   - Análisis de tendencias
   - Dashboards interactivos
   - Alertas automáticas