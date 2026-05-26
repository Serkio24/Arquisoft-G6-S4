"""
Cliente para la API REST de SonarQube.
SonarQube corre en el mismo EC2, puerto 9000, como contenedor Docker.
"""
import os
import httpx
from functools import lru_cache

SONAR_URL = os.getenv("SONAR_URL", "http://localhost:9000")
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "")  # token generado en SonarQube UI
SONAR_PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY", "SprintArq4")


def _auth() -> tuple[str, str]:
    # SonarQube acepta el token como usuario, password vacío
    return (SONAR_TOKEN, "")


def get_maintainability_rating(project_key: str = SONAR_PROJECT_KEY) -> dict:
    """
    Retorna la calificación de mantenibilidad (A-E) del proyecto.
    Métrica: sqale_rating — 1=A, 2=B, 3=C, 4=D, 5=E
    """
    url = f"{SONAR_URL}/api/measures/component"
    params = {
        "component": project_key,
        "metricKeys": "sqale_rating,sqale_index,sqale_debt_ratio,code_smells",
    }
    response = httpx.get(url, params=params, auth=_auth(), timeout=10)
    response.raise_for_status()
    return response.json()


def get_project_status(project_key: str = SONAR_PROJECT_KEY) -> dict:
    """
    Retorna si el Quality Gate pasó o falló en el último análisis.
    Un Quality Gate con condición sqale_rating <= 1 garantiza calificación A.
    """
    url = f"{SONAR_URL}/api/qualitygates/project_status"
    params = {"projectKey": project_key}
    response = httpx.get(url, params=params, auth=_auth(), timeout=10)
    response.raise_for_status()
    return response.json()


def get_analysis_history(project_key: str = SONAR_PROJECT_KEY, page_size: int = 20) -> dict:
    """
    Historial de análisis del proyecto.
    Útil para calcular el porcentaje de análisis con calificación A (ASR: 95%).
    """
    url = f"{SONAR_URL}/api/project_analyses/search"
    params = {"project": project_key, "ps": page_size}
    response = httpx.get(url, params=params, auth=_auth(), timeout=10)
    response.raise_for_status()
    return response.json()


def trigger_analysis(project_key: str = SONAR_PROJECT_KEY) -> dict:
    """
    Dispara un análisis manual desde la API.
    En producción esto lo hace CodeBuild automáticamente en cada push a main.
    Este endpoint es para uso administrativo o debugging.
    """
    url = f"{SONAR_URL}/api/ce/submit"
    data = {"projectKey": project_key}
    response = httpx.post(url, data=data, auth=_auth(), timeout=30)
    response.raise_for_status()
    return response.json()
