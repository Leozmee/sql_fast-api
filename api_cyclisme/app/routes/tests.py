from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
import csv
import io

from app.db.database import get_db
from app.models.user import User
from app.models.athlete import Athlete
from app.models.test import Test, TestType
from app.models.performance_data import PerformanceData
from app.schemas.test import TestCreate, TestRead, TestUpdate
from app.schemas.performance import PerformanceDataCreate, PerformanceDataRead
from app.auth.jwt import get_current_user, get_current_staff_user

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

@router.post("/", response_model=TestRead, status_code=status.HTTP_201_CREATED)
def create_test(
    test_data: TestCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée un nouveau test pour un athlète.
    """
    # Vérification que l'athlète existe et appartient à l'utilisateur
    athlete = db.get(Athlete, test_data.athlete_id)
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
    
    # Création du test
    new_test = Test(
        athlete_id=test_data.athlete_id,
        test_type=test_data.test_type.value,
        test_date=test_data.test_date,
        weight=test_data.weight,
        height=test_data.height,
        max_power=test_data.max_power,
        vo2max=test_data.vo2max,
        notes=test_data.notes
    )
    
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return new_test

@router.get("/", response_model=List[TestRead])
def read_tests(
    athlete_id: Optional[UUID] = None,
    test_type: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des tests, éventuellement filtrés par athlète et/ou type de test.
    """
    query = select(Test)
    
    # Appliquer les filtres
    if athlete_id:
        query = query.where(Test.athlete_id == athlete_id)
    
    if test_type:
        query = query.where(Test.test_type == test_type)
    
    # Filtre de sécurité pour les non-admins
    if not current_user.is_staff:
        # Sous-requête pour obtenir les IDs des athlètes de l'utilisateur
        athlete_ids = db.exec(
            select(Athlete.id).where(Athlete.user_id == current_user.id)
        ).all()
        query = query.where(Test.athlete_id.in_(athlete_ids))
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    tests = db.exec(query).all()
    return tests

@router.get("/{test_id}", response_model=TestRead)
def read_test(
    test_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les informations d'un test par son ID.
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    return test

@router.put("/{test_id}", response_model=TestRead)
def update_test(
    test_id: UUID, 
    test_data: TestUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour les informations d'un test.
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Mise à jour des champs
    test_data_dict = test_data.dict(exclude_unset=True)
    
    # Conversion de l'enum en string si nécessaire
    if "test_type" in test_data_dict and test_data_dict["test_type"]:
        test_data_dict["test_type"] = test_data_dict["test_type"].value
    
    for key, value in test_data_dict.items():
        setattr(test, key, value)
    
    db.commit()
    db.refresh(test)
    
    return test

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(
    test_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime un test.
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    db.delete(test)
    db.commit()
    
    return None

@router.post("/{test_id}/performance", response_model=PerformanceDataRead)
def add_performance_data(
    test_id: UUID,
    performance_data: PerformanceDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ajoute une entrée de données de performance à un test.
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Création de la donnée de performance
    new_performance = PerformanceData(
        test_id=test_id,
        time=performance_data.time,
        power=performance_data.power,
        oxygen=performance_data.oxygen,
        cadence=performance_data.cadence,
        heart_rate=performance_data.heart_rate,
        respiration_freq=performance_data.respiration_freq
    )
    
    db.add(new_performance)
    db.commit()
    db.refresh(new_performance)
    
    return new_performance

@router.get("/{test_id}/performance", response_model=List[PerformanceDataRead])
def get_test_performance_data(
    test_id: UUID,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les données de performance d'un test.
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Récupération des données de performance
    performance_data = db.exec(
        select(PerformanceData)
        .where(PerformanceData.test_id == test_id)
        .order_by(PerformanceData.time)
        .offset(skip)
        .limit(limit)
    ).all()
    
    return performance_data

# routes/tests.py (section améliorée pour l'upload CSV)

@router.post("/{test_id}/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_csv_performance_data(
    test_id: UUID,
    file: UploadFile = File(...),
    calculate_metrics: bool = Query(True, description="Calculer automatiquement les métriques après l'import"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Télécharge et importe un fichier CSV de données de performance pour un test.
    Format attendu: time,Power,Oxygen,Cadence,HR,RF
    
    Paramètres:
    - calculate_metrics: Si True, calcule automatiquement les métriques de performance après l'import
    """
    test = db.get(Test, test_id)
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test non trouvé"
        )
    
    # Vérification des permissions
    athlete = db.get(Athlete, test.athlete_id)
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    # Vérification de l'extension du fichier
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format CSV"
        )
    
    # Lecture et traitement du fichier CSV
    contents = await file.read()
    
    try:
        csv_file = io.StringIO(contents.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)
        
        # Vérification des colonnes requises
        required_cols = ['time', 'Power', 'Oxygen', 'Cadence', 'HR', 'RF']
        headers = csv_reader.fieldnames
        
        if not all(col in headers for col in required_cols):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le CSV doit contenir les colonnes: {', '.join(required_cols)}"
            )
        
        # Préparation des données pour insertion par lots
        performance_data_list = []
        
        for row in csv_reader:
            try:
                performance_data = PerformanceData(
                    test_id=test_id,
                    time=int(row['time']),
                    power=float(row['Power']),
                    oxygen=float(row['Oxygen']),
                    cadence=float(row['Cadence']),
                    heart_rate=float(row['HR']),
                    respiration_freq=float(row['RF'])
                )
                performance_data_list.append(performance_data)
            except (ValueError, KeyError) as e:
                # On continue même si une ligne pose problème
                continue
        
        # Insertion des données par lots
        db.add_all(performance_data_list)
        db.commit()
        
        # Calcul automatique des métriques si demandé
        if calculate_metrics and performance_data_list:
            test.calculate_metrics(db)
            
        return {
            "detail": f"Importé {len(performance_data_list)} lignes de données de performance",
            "metrics_calculated": calculate_metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'importation du CSV: {str(e)}"
        )


performance_router = APIRouter(
    prefix="/performance",
    tags=["Performance Data"]
)

@performance_router.get("/{performance_id}", response_model=PerformanceDataRead)
def get_performance_data(
    performance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère une entrée de données de performance par son ID.
    """
    performance = db.get(PerformanceData, performance_id)
    
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donnée de performance non trouvée"
        )
    
    # Vérification des permissions
    test = db.get(Test, performance.test_id)
    athlete = db.get(Athlete, test.athlete_id)
    
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    return performance

@performance_router.delete("/{performance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_data(
    performance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une entrée de données de performance.
    """
    performance = db.get(PerformanceData, performance_id)
    
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donnée de performance non trouvée"
        )
    
    # Vérification des permissions
    test = db.get(Test, performance.test_id)
    athlete = db.get(Athlete, test.athlete_id)
    
    if athlete.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions nécessaires"
        )
    
    db.delete(performance)
    db.commit()
    
    return None