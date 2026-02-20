from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models, crud
from .auth import get_current_user

router = APIRouter(prefix="/leave", tags=["Leave Management"])

@router.get("/balances")
def get_leave_balances(current_user: models.User = Depends(get_current_user)):
    return {
        'Annual': 12.0,
        'Sick': 6.0,
        'Casual': 3.0,
        'Special': 5.0,
    }

@router.get("/history", response_model=list[schemas.HistoryResponse])
def get_leave_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.HistoryItem).filter(
        models.HistoryItem.user_id == current_user.id,
        models.HistoryItem.type == "Leave"
    ).all()

@router.post("/request", response_model=schemas.HistoryResponse)
def submit_leave_request(
        item: schemas.HistoryBase,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    # 1. Convert Pydantic model to a Python dictionary
    item_data = item.model_dump()

    # 2. Overwrite the 'type' and add the 'user_id' inside the dictionary
    item_data["type"] = "Leave"
    item_data["user_id"] = current_user.id

    # 3. Create the database object cleanly
    db_item = models.HistoryItem(**item_data)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/approve/{item_id}", response_model=schemas.HistoryResponse)
def update_leave_status(
    item_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):

    # 1. AUTH CHECK: Run this first
    if current_user.role != "admin":
        print(f"SECURITY: User {current_user.email} denied access (Role: {current_user.role})")
        raise HTTPException(
            status_code=403,  # Use the direct integer to prevent 500 errors
            detail="Only administrators can perform this action"
        )

    # 2. FIND THE ITEM (Moved outside the IF block so Admin can reach it)
    db_item = db.query(models.HistoryItem).filter(
        models.HistoryItem.id == item_id,
        models.HistoryItem.type == "Leave" # Ensuring we only approve Leave items
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail=f"Leave request with ID {item_id} not found")

    # 3. UPDATE
    db_item.status = status
    db.commit()
    db.refresh(db_item)
    return db_item
