from pyclbr import Function
from pydoc import describe
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta

from app.db.database import get_db
from app.models.user import User
from app.models.athlete import Athlete
from app.models.test import Test
from app.schemas.test import TestStats
from app.auth.jwt import get_current_user

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)

@router.get("/performance-metrics", response_model=dict)
def get_global_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: Optional[int] = Query(None, description="Nombre de jours passés à inclure")
):
    """
    Fournit des métriques globales de performance pour tous les athlètes de l'utilisateur
    ou pour tous les athlètes si l'utilisateur est un membre du staff.
    
    Paramètres optionnels :
    - days: Limite les résultats aux tests effectués dans les X derniers jours
    """
    from sqlalchemy import func, desc
    
    # Filtre des athlètes selon les permissions
    if current_user.is_staff:
        athlete_filter = True  # Pas de filtre pour les admins
    else:
        athlete_filter = Athlete.user_id == current_user.id
    
    # Filtre de date si spécifié
    date_filter = True
    if days is not None:
        cutoff_date = date.today() - timedelta(days=days)
        date_filter = Test.test_date >= cutoff_date
    
    # 1. Athlète avec la VO2max la plus élevée
    best_vo2max_query = (
        select(
            Athlete.id,
            Athlete.first_name,
            Athlete.last_name,
            func.max(Test.vo2max).label("max_vo2max")
        )
        .join(Test, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(date_filter)
        .where(Test.vo2max != None)
        .group_by(Athlete.id)
        .order_by(desc("max_vo2max"))
        .limit(1)
    )
    
    best_vo2max = db.exec(best_vo2max_query).first()
    
    # 2. Athlète avec la puissance moyenne la plus élevée
    best_power_query = (
        select(
            Athlete.id,
            Athlete.first_name,
            Athlete.last_name,
            func.max(Test.avg_power).label("max_avg_power")
        )
        .join(Test, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(date_filter)
        .where(Test.avg_power != None)
        .group_by(Athlete.id)
        .order_by(desc("max_avg_power"))
        .limit(1)
    )
    
    best_power = db.exec(best_power_query).first()
    
    # 3. Meilleur rapport poids/puissance
    best_power_weight_query = (
        select(
            Athlete.id,
            Athlete.first_name,
            Athlete.last_name,
            func.max(Test.power_weight_ratio).label("max_power_weight_ratio")
        )
        .join(Test, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(date_filter)
        .where(Test.power_weight_ratio != None)
        .group_by(Athlete.id)
        .order_by(desc("max_power_weight_ratio"))
        .limit(1)
    )
    
    best_power_weight = db.exec(best_power_weight_query).first()
    
    # 4. Statistiques globales
    global_stats_query = (
        select(
            func.avg(Test.vo2max).label("avg_vo2max"),
            func.avg(Test.avg_power).label("avg_power"),
            func.avg(Test.power_weight_ratio).label("avg_power_weight"),
            func.count(Test.id).label("total_tests")
        )
        .join(Athlete, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(date_filter)
    )
    
    global_stats = db.exec(global_stats_query).first()
    
    # Préparation du résultat
    result = {
        "best_vo2max": None,
        "most_powerful": None,
        "best_power_weight_ratio": None,
        "global_stats": {
            "avg_vo2max": round(global_stats[0], 2) if global_stats[0] else None,
            "avg_power": round(global_stats[1], 2) if global_stats[1] else None,
            "avg_power_weight": round(global_stats[2], 2) if global_stats[2] else None,
            "total_tests": global_stats[3]
        }
    }
    
    if best_vo2max:
        result["best_vo2max"] = {
            "id": str(best_vo2max[0]),
            "name": f"{best_vo2max[1]} {best_vo2max[2]}",
            "vo2max": round(best_vo2max[3], 2)
        }
    
    if best_power:
        result["most_powerful"] = {
            "id": str(best_power[0]),
            "name": f"{best_power[1]} {best_power[2]}",
            "avg_power": round(best_power[3], 2)
        }
    
    if best_power_weight:
        result["best_power_weight_ratio"] = {
            "id": str(best_power_weight[0]),
            "name": f"{best_power_weight[1]} {best_power_weight[2]}",
            "power_weight_ratio": round(best_power_weight[3], 2)
        }
    
    return result

@router.get("/tests/top", response_model=List[TestStats])
def get_top_tests(
    metric: str = Query(..., description="Métrique à utiliser: vo2max, max_power, avg_power, power_weight_ratio"),
    limit: int = Query(5, description="Nombre de résultats à retourner"),
    test_type: Optional[str] = Query(None, description="Type de test à filtrer"),
    days: Optional[int] = Query(None, description="Nombre de jours passés à inclure"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les meilleurs tests selon une métrique spécifique.
    
    Métriques disponibles :
    - vo2max : Consommation maximale d'oxygène
    - max_power : Puissance maximale
    - avg_power : Puissance moyenne
    - power_weight_ratio : Rapport puissance/poids
    """
    from sqlalchemy import desc
    
    # Vérifier que la métrique est valide
    valid_metrics = ["vo2max", "max_power", "avg_power", "power_weight_ratio"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Métrique invalide. Utilisez une de ces valeurs: {', '.join(valid_metrics)}"
        )
    
    # Construire la requête de base
    query = (
        select(
            Test.id.label("test_id"),
            Test.athlete_id,
            (Athlete.first_name + " " + Athlete.last_name).label("athlete_name"),
            Test.test_type,
            Test.test_date,
            Test.max_power,
            Test.avg_power,
            Test.power_weight_ratio,
            Test.vo2max
        )
        .join(Athlete, Test.athlete_id == Athlete.id)
    )
    
    # Filtre des athlètes selon les permissions
    if not current_user.is_staff:
        query = query.where(Athlete.user_id == current_user.id)
    
    # Appliquer les filtres additionnels
    if test_type:
        query = query.where(Test.test_type == test_type)
    
    if days:
        cutoff_date = date.today() - timedelta(days=days)
        query = query.where(Test.test_date >= cutoff_date)
    
    # Filtrer les tests avec la métrique spécifiée non null
    query = query.where(getattr(Test, metric) != None)
    
    # Trier par la métrique et limiter les résultats
    query = query.order_by(desc(getattr(Test, metric))).limit(limit)
    
    # Exécuter la requête
    results = db.exec(query).all()
    
    return results

@router.get("/athlete/{athlete_id}/progress", response_model=dict)
def get_athlete_progress(
    athlete_id: UUID,
    metric: str = Query(..., description="Métrique à suivre: vo2max, max_power, avg_power, power_weight_ratio"),
    test_type: Optional[str] = Query(None, description="Type de test à filtrer"),
    days: Optional[int] = Query(90, description="Nombre de jours passés à inclure"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère l'évolution des performances d'un athlète au fil du temps pour une métrique donnée.
    """
    # Vérifier que la métrique est valide
    valid_metrics = ["vo2max", "max_power", "avg_power", "power_weight_ratio"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Métrique invalide. Utilisez une de ces valeurs: {', '.join(valid_metrics)}"
        )
    
    # Vérifier que l'athlète existe
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )
    
    # Vérifier les permissions
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Construire la requête
    query = (
        select(
            Test.test_date,
            Test.test_type,
            getattr(Test, metric).label("value")
        )
        .where(Test.athlete_id == athlete_id)
        .where(getattr(Test, metric) != None)
    )
    
    # Appliquer les filtres additionnels
    if test_type:
        query = query.where(Test.test_type == test_type)
    
    if days:
        cutoff_date = date.today() - timedelta(days=days)
        query = query.where(Test.test_date >= cutoff_date)
    
    # Trier par date
    query = query.order_by(Test.test_date)
    
    # Exécuter la requête
    results = db.exec(query).all()
    
    # Formater les résultats pour un affichage graphique
    data_points = [
        {
            "date": result.test_date.isoformat(),
            "test_type": result.test_type,
            "value": round(result.value, 2)
        }
        for result in results
    ]
    
    # Calculer la tendance (amélioration ou détérioration)
    trend = None
    if len(data_points) >= 2:
        first_value = data_points[0]["value"]
        last_value = data_points[-1]["value"]
        change = last_value - first_value
        percent_change = (change / first_value * 100) if first_value else 0
        
        trend = {
            "absolute_change": round(change, 2),
            "percent_change": round(percent_change, 2),
            "is_improving": change > 0
        }
    
    return {
        "athlete_id": str(athlete_id),
        "athlete_name": f"{athlete.first_name} {athlete.last_name}",
        "metric": metric,
        "data": data_points,
        "trend": trend
    }

@router.get("/comparison")
def compare_athletes(
    athlete_ids: List[UUID] = Query(..., description="Liste des IDs d'athlètes à comparer"),
    metric: str = Query(..., description="Métrique à comparer: vo2max, max_power, avg_power, power_weight_ratio"),
    test_type: Optional[str] = Query(None, description="Type de test à filtrer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare les performances de plusieurs athlètes sur une métrique donnée.
    Parfait pour l'intégration avec des visualisations dans Power BI ou Streamlit.
    """
    # Vérifier que la métrique est valide
    valid_metrics = ["vo2max", "max_power", "avg_power", "power_weight_ratio"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Métrique invalide. Utilisez une de ces valeurs: {', '.join(valid_metrics)}"
        )
    
    # Vérifier les permissions pour chaque athlète
    for athlete_id in athlete_ids:
        athlete = db.get(Athlete, athlete_id)
        if not athlete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Athlète avec ID {athlete_id} non trouvé"
            )
        
        if athlete.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Vous n'avez pas les permissions pour accéder à l'athlète {athlete_id}"
            )
    
    # Récupérer les données pour chaque athlète
    comparison_data = []
    
    for athlete_id in athlete_ids:
        # Récupérer l'athlète
        athlete = db.get(Athlete, athlete_id)
        
        # Construire la requête pour obtenir la valeur maximale de la métrique
        query = (
            select(
                Function.max(getattr(Test, metric)).label("best_value")
            )
            .where(Test.athlete_id == athlete_id)
        )
        
        # Appliquer le filtre de type de test si spécifié
        if test_type:
            query = query.where(Test.test_type == test_type)
        
        # Exécuter la requête
        result = db.exec(query).first()
        
        best_value = result.best_value if result and result.best_value else None
        
        # Récupérer les dernières performances
        recent_query = (
            select(
                Test.test_date,
                Test.test_type,
                getattr(Test, metric).label("value")
            )
            .where(Test.athlete_id == athlete_id)
            .where(getattr(Test, metric) != None)
        )
        
        if test_type:
            recent_query = recent_query.where(Test.test_type == test_type)
        
        recent_query = recent_query.order_by(describe(Test.test_date)).limit(3)
        recent_tests = db.exec(recent_query).all()
        
        # Ajouter à la comparaison
        comparison_data.append({
            "athlete_id": str(athlete_id),
            "athlete_name": f"{athlete.first_name} {athlete.last_name}",
            "best_value": round(best_value, 2) if best_value else None,
            "recent_tests": [
                {
                    "date": test.test_date.isoformat(),
                    "test_type": test.test_type,
                    "value": round(test.value, 2)
                }
                for test in recent_tests
            ]
        })
    
    return {
        "metric": metric,
        "test_type": test_type,
        "athletes": comparison_data
    }