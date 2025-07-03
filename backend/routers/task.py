from fastapi import APIRouter, HTTPException, Depends
from schemas import TransportTaskSummary
from sqlalchemy import func
from typing import List
from database import get_db
from sqlalchemy.orm import Session
from models import TransportTask
from typing import List

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TransportTaskSummary])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(TransportTask).order_by(TransportTask.date_creation.desc()).all()



@router.get("/recent", response_model=List[TransportTaskSummary])
def get_recent_tasks(db: Session = Depends(get_db)):
    tasks = (
        db.query(TransportTask)
        .order_by(
            func.coalesce(TransportTask.date_derniere_maj, TransportTask.date_creation).desc()
        )
        .limit(5)
        .all()
    )
    return tasks

@router.get("/{task_id}", response_model=TransportTaskSummary)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task