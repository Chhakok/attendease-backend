import os
import shutil
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .. import schemas, database, models, security

router = APIRouter(prefix="/auth", tags=["Authentication"])

# This MUST point to the exact login path for the button to work
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    print(f"DEBUG: Found user {user.email if user else 'None'} with role {user.role if user else 'N/A'}")

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",

        )
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=schemas.User)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Returns the profile details of the currently authenticated user."""
    return current_user


# --- NEW: Safe Profile Update Route ---
@router.put("/profile", response_model=schemas.User)
def update_profile(
        phone_number: str = Form(None),
        file: UploadFile = File(None),
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)  # Uses your exact function
):
    """Updates the user's phone number and/or profile picture."""

    # Update phone number if provided
    if phone_number is not None:
        current_user.phone_number = phone_number

    # Update image if provided
    if file is not None:
        # 1. Create directory safely
        os.makedirs("static/avatars", exist_ok=True)

        # 2. Extract extension and create a unique name (e.g., user_1_avatar.jpg)
        file_extension = file.filename.split(".")[-1]
        filename = f"user_{current_user.id}_avatar.{file_extension}"
        file_path = f"static/avatars/{filename}"

        # 3. Save the actual file to the computer/server
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Save the new URL path to the database
        # Make sure this matches the alias in your Pydantic schema (avatar_url vs avatar)
        current_user.avatar_url = f"/{file_path}"

    db.commit()
    db.refresh(current_user)
    return current_user

