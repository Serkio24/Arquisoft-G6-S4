# ms-quality-analysis

Microservicio de análisis de calidad y mantenibilidad de BITE.co.

Expone métricas de SonarQube via REST API y garantiza el cumplimiento del ASR de mantenibilidad mediante un pipeline CI/CD en AWS CodeBuild.

## Estructura

```
ms-quality-analysis/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── api/
│   │   ├── health.py            # GET /health
│   │   └── quality.py           # GET /quality/status, /quality/asr, etc.
│   ├── core/
│   │   ├── sonarqube_client.py  # Cliente HTTP para SonarQube API
│   │   └── asr_evaluator.py     # Lógica de evaluación del ASR
│   └── schemas/
│       └── quality.py           # Modelos Pydantic
├── tests/
│   └── test_quality_api.py
├── Dockerfile
├── docker-compose.yml           # Levanta FastAPI + SonarQube + PostgreSQL
├── buildspec.yml                # Pipeline AWS CodeBuild
├── requirements.txt
└── .env.example
```

## Cómo corre en producción (AWS)

```
Git push a main
      │
      ▼
AWS CodeBuild (buildspec.yml)
      │
      ├── 1. Corre tests (pytest)
      ├── 2. Ejecuta SonarScanner → SonarQube analiza el código
      ├── 3. Espera Quality Gate → si falla, el build falla (bloquea deploy)
      ├── 4. Build imagen Docker → push a ECR
      └── 5. Deploy en EC2 via SSM
```

## Endpoints disponibles (via Kong en /quality)

| Método | Path                  | Descripción                              |
|--------|-----------------------|------------------------------------------|
| GET    | /quality/status       | Estado actual del Quality Gate           |
| GET    | /quality/asr          | Evaluación del ASR (cumple 95%?)         |
| GET    | /quality/metrics      | Métricas detalladas de mantenibilidad    |
| GET    | /quality/history      | Historial de análisis                    |
| POST   | /quality/analyze      | Disparar análisis manual (admin)         |
| GET    | /health               | Health check para Kong                   |

## Desarrollo local

```bash
# 1. Copiar variables de entorno
cp .env.example .env
# Editar .env con tu token de SonarQube

# 2. Levantar todo
docker-compose up -d

# 3. Esperar ~2 min a que SonarQube inicie, luego abrir:
#    http://localhost:9000 → crear proyecto → obtener token → poner en .env

# 4. Reiniciar la API con el token
docker-compose restart quality-analysis-api

# 5. Probar
curl http://localhost:8080/health
curl http://localhost:8080/quality/status
```

## Quality Gate recomendado en SonarQube

Crear un Quality Gate llamado "ASR-Mantenibilidad" con la condición:

- **Métrica**: Maintainability Rating (`sqale_rating`)  
- **Operador**: is worse than  
- **Valor**: A (1)

Asignarlo al proyecto `bite-monorepo`. Así cualquier análisis que baje de A hace fallar el pipeline.

## Variables de entorno

| Variable           | Descripción                          | Default             |
|--------------------|--------------------------------------|---------------------|
| `SONAR_URL`        | URL de SonarQube                     | http://localhost:9000 |
| `SONAR_TOKEN`      | Token de autenticación               | (requerido)         |
| `SONAR_PROJECT_KEY`| Clave del proyecto en SonarQube      | bite-monorepo       |
