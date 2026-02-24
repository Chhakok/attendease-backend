from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


# --- History & Attendance ---
class HistoryBase(BaseModel):
    # type: str
    type: Optional[str] = None
    date: str
    title: str
    subtitle: str
    status: str
    # Maps 'minutes_worked' (DB) to 'minutesWorked' (JSON/Flutter)
    minutes_worked: int = Field(..., alias="minutesWorked")

    class Config:
        populate_by_name = True


class HistoryResponse(HistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True



# --- User & Auth ---
class UserBase(BaseModel):
    email: EmailStr
    name: str
    position: str
    role: str
    # Syncs DB 'phone_number' with Flutter 'phoneNumber'
    phone_number: str = Field(..., alias="phoneNumber")
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    # Syncs DB 'avatar_url' with Flutter 'avatarUrl'
    # avatar_url: str = Field("assets/images/profile.jpg", alias="avatarUrl")
    avatar_url: Optional[str] = Field(default="assets/images/profile.jpg", alias="avatarUrl")

    class Config:
        from_attributes = True
        populate_by_name = True

# CRITICAL FIX: Add this so the router @router.get("/me", response_model=schemas.User) works
User = UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str



