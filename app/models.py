from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    position = Column(String)
    # Corrected: Use 'phone_number' to match Flutter's 'phoneNumber' JSON logic
    phone_number = Column(String)
    # Corrected: Use 'avatar_url' to match typical Flutter naming
    avatar_url = Column(String, nullable=True)
    # avatar_url = Column(String, default="assets/images/profile.jpg")
    # ADD THIS: Role can be 'employee' or 'admin'
    role = Column(String, default="employee")
    history = relationship("HistoryItem", back_populates="owner")

class HistoryItem(Base):
    __tablename__ = "history_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="history")
    type = Column(String)      # 'Attendance' or 'Leave'
    date = Column(String)      # Store as YYYY-MM-DD
    title = Column(String)     # e.g., 'Checked In' or 'Annual Leave'
    subtitle = Column(String)  # e.g., '09:00 AM - 05:00 PM'
    status = Column(String)    # 'OnTime', 'Approved', etc.
    minutes_worked = Column(Integer, default=0) # Maps to 'minutesWorked'