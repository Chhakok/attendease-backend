from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import re
from .. import schemas, database, models, crud
from .auth import get_current_user

router = APIRouter(prefix="/leave", tags=["Leave Management"])


@router.get("/balances")
def get_leave_balances(
        db: Session = Depends(database.get_db),  # <--- ADD DB DEPENDENCY
        current_user: models.User = Depends(get_current_user)
):
    # 1. Start with the Base Annual Limits
    balances = {
        'Annual': 12.0,
        'Sick': 6.0,
        'Casual': 3.0,
        'Special': 5.0,
    }

    # 2. Get all leaves the user has requested from the Database
    past_leaves = db.query(models.HistoryItem).filter(
        models.HistoryItem.user_id == current_user.id,
        models.HistoryItem.type == "Leave"
    ).all()

    # 3. Mathematically deduct the days they have already used
    for leave in past_leaves:
        # The title looks like "Annual Leave", so we strip the word " Leave" to get "Annual"
        leave_type = leave.title.replace(" Leave", "")

        if leave_type in balances:
            # We use regex to extract the "1.5" out of the subtitle string: "Reason (1.5 day(s) • Full Day)"
            match = re.search(r'\(([\d.]+)\s*day', leave.subtitle)
            if match:
                days_used = float(match.group(1))
                balances[leave_type] -= days_used

    return balances

@router.get("/history", response_model=list[schemas.HistoryResponse])
def get_leave_history(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.HistoryItem).filter(
        models.HistoryItem.user_id == current_user.id,
        models.HistoryItem.type == "Leave"
    ).order_by(models.HistoryItem.date.desc()).offset(skip).limit(limit).all()



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


# ==========================================
# TESTING TOOL: DELETE LEAVE REQUEST
# ==========================================
@router.delete("/{item_id}")
def delete_leave_request(
        item_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Deletes a Leave record. Used for clearing test data and refunding leave balances.
    """
    try:
        # 1. Find the leave record
        db_item = db.query(models.HistoryItem).filter(
            models.HistoryItem.id == item_id,
            models.HistoryItem.user_id == current_user.id
        ).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Leave record not found")

        # 2. Delete and save
        db.delete(db_item)
        db.commit()

        return {"message": f"Successfully deleted leave request {item_id}"}

    except Exception as e:
        # X-Ray: Catches crashes and prints them to Swagger UI!
        print(f"CRASH ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Crash: {str(e)}")

