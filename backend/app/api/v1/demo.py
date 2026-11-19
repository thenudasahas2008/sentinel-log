from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.demo_generator import DemoDataGenerator

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

@router.post("/generate")
def generate_demo_dataset(db: Session = Depends(get_db)):
    """
    Generates realistic synthetic security events and alerts for demonstration.
    All data is tagged with is_synthetic = True.
    """
    return DemoDataGenerator.generate_demo_scenario(db)

@router.post("/reset")
def reset_demo_dataset(db: Session = Depends(get_db)):
    """
    Purges only synthetic records from the database. Production logs remain intact.
    """
    return DemoDataGenerator.reset_demo_data(db)
