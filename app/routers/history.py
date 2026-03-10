# app/routers/history.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas
from .auth import get_current_user
from sqlalchemy import desc

router = APIRouter(prefix="/history", tags=["Unified History"])


@router.get("/all", response_model=list[schemas.HistoryResponse])
def get_all_activity(
    limit: int = 10, # Default to last 10 items
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.HistoryItem).filter(
        models.HistoryItem.user_id == current_user.id
    ).order_by(models.HistoryItem.id.desc()).limit(limit).all()


