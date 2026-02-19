from sqlalchemy.orm import Session
from . import models, schemas

def create_attendance(db: Session, item: schemas.HistoryBase, user_id: int):
    try:
        db_item = models.HistoryItem(
            user_id=user_id,
            type=item.type,
            date=item.date,
            title=item.title,
            subtitle=item.subtitle,
            status=item.status,
            # USE THE UNDERSCORE VERSION HERE
            minutes_worked=item.minutes_worked
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        print(f"!!! DATABASE ERROR: {e}")
        raise e

def get_user_history(db: Session, user_id: int):
    # Returns all history (Attendance & Leave) for the Flutter history screen
    return db.query(models.HistoryItem).filter(models.HistoryItem.user_id == user_id).all()

