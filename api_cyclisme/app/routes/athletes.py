from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.user import User
from app.models.athlete import Athlete
from app.models.test import Test
from app.models.performance_data import PerformanceData
from app.schemas.athlete import AthleteCreate, AthleteRead, AthleteUpdate
from app.auth.jwt import get_current_user, get_current_staff_user

router = APIRouter(
    prefix="/athletes",
    tags=["Athletes"]
)

@router.post("/", response_model=AthleteRead, status_code=status.HTTP_201_CREATED)
def create_athlete(
    athlete_data: AthleteCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_user)  # Réservé aux membres du staff
):
    """
    Crée un nouvel athlète (réservé aux membres du staff).
    """
    new_athlete = Athlete(
        user_id=current_user.id,  # L'athlète sera associé au membre du staff qui le crée
        first_name=athlete_data.first_name,
        last_name=athlete_data.last_name,
        age=athlete_data.age,
        weight=athlete_data.weight,
        height=athlete_data.height,
        vo2max=athlete_data.vo2max
    )
    
    db.add(new_athlete)
    db.commit()
    db.refresh(new_athlete)
    
    return new_athlete

@router.get("/", response_model=List[AthleteRead])
def read_athletes(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = Query(None, description="Filtre par nom ou prénom"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des athlètes.
    Les utilisateurs normaux voient uniquement leurs propres athlètes.
    Les administrateurs peuvent voir tous les athlètes.
    """
    query = select(Athlete)
    
    
    if name:
        query = query.where(
            (Athlete.first_name.contains(name)) | 
            (Athlete.last_name.contains(name))
        )
    
    
    if not current_user.is_staff:
        query = query.where(Athlete.user_id == current_user.id)
    
    
    query = query.offset(skip).limit(limit)
    
    
    athletes = db.exec(query).all()
    
    return athletes

@router.get("/{athlete_id}", response_model=AthleteRead)
def read_athlete(
    athlete_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les informations d'un athlète par son ID.
    """
    athlete = db.get(Athlete, athlete_id)
    
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )
    
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    return athlete

@router.put("/{athlete_id}", response_model=AthleteRead)
def update_athlete(
    athlete_id: UUID, 
    athlete_data: AthleteUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour les informations d'un athlète.
    """
    athlete = db.get(Athlete, athlete_id)
    
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )
    
    
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    
    athlete_data_dict = athlete_data.dict(exclude_unset=True)
    
    for key, value in athlete_data_dict.items():
        setattr(athlete, key, value)
    
    db.commit()
    db.refresh(athlete)
    
    return athlete

@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_athlete(
    athlete_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_user)  # Réservé aux membres du staff
):
    """
    Supprime un athlète (réservé aux membres du staff).
    """
    athlete = db.get(Athlete, athlete_id)
    
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )
    
    db.delete(athlete)
    db.commit()
    
    return None

@router.get("/{athlete_id}/tests", response_model=List[dict])
def get_athlete_tests(
    athlete_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère tous les tests d'un athlète spécifique.
    """

    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )

    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    query = (
        select(
            Test.id,
            Test.test_type,
            Test.test_date,
            Test.max_power,
            Test.avg_power,
            Test.vo2max,
            Test.power_weight_ratio
        )
        .where(Test.athlete_id == athlete_id)
        .order_by(Test.test_date.desc())
        .offset(skip)
        .limit(limit)
    )
    
    tests = db.exec(query).all()
    
    result = []
    for test in tests:
        result.append({
            "id": str(test[0]),
            "test_type": test[1],
            "test_date": test[2].isoformat() if test[2] else None,
            "max_power": test[3],
            "avg_power": test[4],
            "vo2max": test[5],
            "power_weight_ratio": test[6]
        })
    
    return result

@router.get("/{athlete_id}/summary", response_model=dict)
def get_athlete_summary(
    athlete_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère un résumé des performances d'un athlète, incluant:
    - Nombre total de tests
    - Meilleures performances (VO2max, puissance, etc.)
    - Progression récente
    """
    # Vérifier que l'athlète existe
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Athlète non trouvé"
        )
    
    # Vérification des permissions
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Récupérer le nombre total de tests
    test_count = db.exec(
        select(Test)
        .where(Test.athlete_id == athlete_id)
        .count()
    ).one()
    
    # Récupérer les meilleures performances
    from sqlalchemy import func, desc
    
    best_vo2max_query = (
        select(func.max(Test.vo2max))
        .where(Test.athlete_id == athlete_id)
        .where(Test.vo2max != None)
    )
    
    best_power_query = (
        select(func.max(Test.max_power))
        .where(Test.athlete_id == athlete_id)
        .where(Test.max_power != None)
    )
    
    best_avg_power_query = (
        select(func.max(Test.avg_power))
        .where(Test.athlete_id == athlete_id)
        .where(Test.avg_power != None)
    )
    
    best_power_weight_query = (
        select(func.max(Test.power_weight_ratio))
        .where(Test.athlete_id == athlete_id)
        .where(Test.power_weight_ratio != None)
    )
    
    # Récupérer le dernier test
    last_test_query = (
        select(Test)
        .where(Test.athlete_id == athlete_id)
        .order_by(desc(Test.test_date))
        .limit(1)
    )
    
    # Exécuter les requêtes
    best_vo2max = db.exec(best_vo2max_query).one_or_none()
    best_power = db.exec(best_power_query).one_or_none()
    best_avg_power = db.exec(best_avg_power_query).one_or_none()
    best_power_weight = db.exec(best_power_weight_query).one_or_none()
    last_test = db.exec(last_test_query).first()
    
    # Préparer le résumé
    summary = {
        "athlete_id": str(athlete_id),
        "athlete_name": f"{athlete.first_name} {athlete.last_name}",
        "profile": {
            "age": athlete.age,
            "weight": athlete.weight,
            "height": athlete.height,
            "vo2max": athlete.vo2max
        },
        "test_count": test_count,
        "best_performances": {
            "vo2max": round(best_vo2max, 2) if best_vo2max else None,
            "max_power": round(best_power, 2) if best_power else None,
            "avg_power": round(best_avg_power, 2) if best_avg_power else None,
            "power_weight_ratio": round(best_power_weight, 2) if best_power_weight else None
        },
        "last_test": {
            "id": str(last_test.id) if last_test else None,
            "date": last_test.test_date.isoformat() if last_test and last_test.test_date else None,
            "type": last_test.test_type if last_test else None
        }
    }
    
    return summary

@router.get("/stats/best", response_model=dict)
def get_athlete_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les statistiques des meilleurs athlètes:
    - L'athlète le plus puissant en moyenne
    - L'athlète avec la VO2max la plus élevée
    - L'athlète avec le meilleur rapport poids/puissance
    """
    from sqlalchemy import func, desc
    
    # Filtre des athlètes selon les permissions
    if current_user.is_staff:
        athlete_filter = True  # Pas de filtre pour les admins
    else:
        athlete_filter = Athlete.user_id == current_user.id
    
    # 1. Athlète avec la VO2max la plus élevée
    best_vo2max = db.exec(
        select(Athlete)
        .where(athlete_filter)
        .where(Athlete.vo2max != None)
        .order_by(desc(Athlete.vo2max))
        .limit(1)
    ).first()
    
    # 2. Athlète avec la puissance moyenne la plus élevée
    # Requête complexe pour calculer la puissance moyenne par athlète
    power_query = (
        select(
            Athlete.id,
            Athlete.first_name,
            Athlete.last_name,
            func.avg(Test.avg_power).label("avg_power")
        )
        .join(Test, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(Test.avg_power != None)
        .group_by(Athlete.id)
        .order_by(desc("avg_power"))
        .limit(1)
    )
    
    most_powerful = db.exec(power_query).first()
    
    # 3. Meilleur rapport poids/puissance
    power_weight_query = (
        select(
            Athlete.id,
            Athlete.first_name,
            Athlete.last_name,
            func.avg(Test.power_weight_ratio).label("avg_ratio")
        )
        .join(Test, Test.athlete_id == Athlete.id)
        .where(athlete_filter)
        .where(Test.power_weight_ratio != None)
        .group_by(Athlete.id)
        .order_by(desc("avg_ratio"))
        .limit(1)
    )
    
    best_power_weight = db.exec(power_weight_query).first()
    
    # Préparation du résultat
    result = {
        "best_vo2max": None,
        "most_powerful": None,
        "best_power_weight_ratio": None
    }
    
    if best_vo2max:
        result["best_vo2max"] = {
            "id": str(best_vo2max.id),
            "name": f"{best_vo2max.first_name} {best_vo2max.last_name}",
            "vo2max": best_vo2max.vo2max
        }
    
    if most_powerful:
        result["most_powerful"] = {
            "id": str(most_powerful[0]),
            "name": f"{most_powerful[1]} {most_powerful[2]}",
            "avg_power": round(most_powerful[3], 2) if most_powerful[3] else None
        }
    
    if best_power_weight:
        result["best_power_weight_ratio"] = {
            "id": str(best_power_weight[0]),
            "name": f"{best_power_weight[1]} {best_power_weight[2]}",
            "power_weight_ratio": round(best_power_weight[3], 2) if best_power_weight[3] else None
        }
    
    return result