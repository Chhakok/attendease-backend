
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user


router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/check-in", response_model=schemas.HistoryResponse)
def check_in(
    item: schemas.HistoryBase,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user) # This triggers the "Lock" icon
):
    return crud.create_attendance(db=db, item=item, user_id=current_user.id)


@router.get("/history", response_model=List[schemas.HistoryResponse])
def get_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.HistoryItem).filter(
        models.HistoryItem.user_id == current_user.id,
        models.HistoryItem.type == "Attendance"
    ).all()
    return crud.get_user_history(db=db, user_id=current_user.id)

@router.patch("/check-out/{item_id}", response_model=schemas.HistoryResponse)
def check_out(
        item_id: int,
        end_time: str,  # Example: "05:00 PM"
        status: str,
        minutes_worked: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    # 1. Find the existing morning record
    db_item = db.query(models.HistoryItem).filter(
        models.HistoryItem.id == item_id,
        models.HistoryItem.user_id == current_user.id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Check-in record not found")

    # 2. Update the subtitle string (e.g., "09:00 AM - 05:00 PM")
    start_time = db_item.subtitle.split(" - ")[0]
    db_item.subtitle = f"{start_time} - {end_time}"
    db_item.status = status
    db_item.title = "Shift Completed"
    db_item.minutes_worked = minutes_worked

    db.commit()
    db.refresh(db_item)
    return db_item



# ==========================================
# TESTING TOOL: DELETE ENDPOINT
# ==========================================
@router.delete("/{item_id}")
def delete_attendance(
        item_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    try:
        db_item = db.query(models.HistoryItem).filter(
            models.HistoryItem.id == item_id,
            models.HistoryItem.user_id == current_user.id
        ).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Record not found")

        # Delete and save
        db.delete(db_item)
        db.commit()

        return {"message": f"Successfully deleted item {item_id}"}

    except Exception as e:
        # If Python crashes, it will print the EXACT error text to your Swagger UI!
        print(f"CRASH ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Crash: {str(e)}")