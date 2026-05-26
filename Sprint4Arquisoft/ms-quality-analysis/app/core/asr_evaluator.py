"""
Evaluador del ASR de mantenibilidad.

ASR: "Mantener calificación A en mantenibilidad (sqale_rating=1) 
      en el 95% de los análisis sobre la rama principal."

Este módulo toma el historial de SonarQube y calcula si se está 
cumpliendo el umbral del 95%.
"""
from app.core.sonarqube_client import get_analysis_history, get_maintainability_rating, get_project_status

# Letra A equivale a sqale_rating = "1" en SonarQube
RATING_A = "1"
ASR_THRESHOLD_PERCENT = 95.0


def evaluate_asr_compliance(project_key: str) -> dict:
    """
    Calcula el cumplimiento del ASR comparando cuántos análisis
    recientes obtuvieron calificación A versus el total.
    
    SonarQube guarda el sqale_rating por análisis en su historial.
    """
    history = get_analysis_history(project_key, page_size=50)
    analyses = history.get("analyses", [])

    if not analyses:
        return {
            "compliant": False,
            "reason": "No hay análisis registrados aún",
            "percent_a": 0.0,
            "threshold": ASR_THRESHOLD_PERCENT,
            "total_analyses": 0,
        }

    # Contamos los análisis que tienen el evento "Quality Gate" en estado OK
    # SonarQube marca el Quality Gate como OK cuando sqale_rating <= A
    passed = 0
    for analysis in analyses:
        events = analysis.get("events", [])
        for event in events:
            if event.get("category") == "QUALITY_GATE" and event.get("name") == "Green (was Red)":
                passed += 1
                break
            if event.get("category") == "QUALITY_GATE" and "Green" in event.get("name", ""):
                passed += 1
                break

    total = len(analyses)
    percent = (passed / total) * 100 if total > 0 else 0.0
    compliant = percent >= ASR_THRESHOLD_PERCENT

    return {
        "compliant": compliant,
        "percent_a": round(percent, 2),
        "threshold": ASR_THRESHOLD_PERCENT,
        "total_analyses": total,
        "analyses_with_rating_a": passed,
        "status": "CUMPLE ASR" if compliant else "NO CUMPLE ASR",
    }


def get_current_rating(project_key: str) -> dict:
    """
    Rating actual del proyecto en este momento.
    """
    raw = get_maintainability_rating(project_key)
    measures = raw.get("component", {}).get("measures", [])

    result = {}
    rating_map = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}

    for measure in measures:
        key = measure["metric"]
        value = measure.get("value", "N/A")
        if key == "sqale_rating":
            result["rating"] = rating_map.get(value, value)
            result["rating_raw"] = value
            result["is_a"] = value == RATING_A
        elif key == "sqale_index":
            result["technical_debt_minutes"] = value
        elif key == "sqale_debt_ratio":
            result["debt_ratio_percent"] = value
        elif key == "code_smells":
            result["code_smells"] = value

    return result
