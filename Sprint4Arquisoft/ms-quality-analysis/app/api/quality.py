"""
Endpoints del microservicio de calidad.
Kong los expone bajo el path /quality (ej: http://kong:8000/quality/status)
"""
from fastapi import APIRouter, HTTPException, Query
from app.core import sonarqube_client, asr_evaluator
import os

router = APIRouter(tags=["quality"])

PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY", "bite-monorepo")


@router.get("/status")
def get_quality_status():
    """
    Estado actual del Quality Gate en SonarQube.
    Retorna si el último análisis pasó o falló.
    """
    try:
        gate = sonarqube_client.get_project_status(PROJECT_KEY)
        rating = asr_evaluator.get_current_rating(PROJECT_KEY)
        return {
            "project": PROJECT_KEY,
            "quality_gate": gate.get("projectStatus", {}),
            "maintainability": rating,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error consultando SonarQube: {str(e)}")


@router.get("/asr")
def get_asr_compliance():
    """
    Evalúa si el proyecto cumple el ASR de mantenibilidad:
    calificación A en el 95% de los análisis sobre main.
    
    Este endpoint es el que el equipo revisa para saber si están
    cumpliendo el requerimiento arquitectónico.
    """
    try:
        compliance = asr_evaluator.evaluate_asr_compliance(PROJECT_KEY)
        current = asr_evaluator.get_current_rating(PROJECT_KEY)
        return {
            "project": PROJECT_KEY,
            "asr_evaluation": compliance,
            "current_rating": current,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error evaluando ASR: {str(e)}")


@router.get("/metrics")
def get_metrics(project: str = Query(default=None)):
    """
    Métricas detalladas de mantenibilidad.
    Acepta ?project=<key> para consultar proyectos específicos.
    """
    key = project or PROJECT_KEY
    try:
        return sonarqube_client.get_maintainability_rating(key)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error obteniendo métricas: {str(e)}")


@router.get("/history")
def get_analysis_history(limit: int = Query(default=20, le=50)):
    """
    Historial de los últimos análisis. Útil para ver tendencias
    y calcular el porcentaje de cumplimiento del ASR manualmente.
    """
    try:
        return sonarqube_client.get_analysis_history(PROJECT_KEY, page_size=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error obteniendo historial: {str(e)}")


@router.post("/analyze")
def trigger_manual_analysis():
    """
    Dispara un análisis manual. Solo para uso administrativo.
    En producción, CodeBuild lo hace automáticamente en cada push a main.
    """
    try:
        result = sonarqube_client.trigger_analysis(PROJECT_KEY)
        return {"message": "Análisis iniciado", "task": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error disparando análisis: {str(e)}")
