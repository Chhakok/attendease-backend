import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models, database, security
from .routers import auth, attendance, leave, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Tables
    print("--- SYSTEM: Booting Up and Creating Tables ---")
    models.Base.metadata.create_all(bind=database.engine)

    db = database.SessionLocal()
    try:
        # 2. Seed or Update Test Employee (Heng Sovann)
        test_email = "test@example.com"
        test_user = db.query(models.User).filter(models.User.email == test_email).first()
        hashed = security.get_password_hash("password123")

        if not test_user:
            print("--- SEEDING: Creating Test Employee ---")
            db.add(models.User(
                name="Heng Sovann",
                email=test_email,
                hashed_password=hashed,
                position="Senior Flutter Dev",
                phone_number="+855 12 999 888",
                role="employee"
            ))
        else:
            print("--- SEEDING: Updating Test Employee ---")
            test_user.name = "Heng Sovann"
            test_user.hashed_password = hashed
            test_user.position = "Senior Flutter Dev"
            test_user.phone_number = "+855 12 999 888"

        # 3. Seed or Update HR Manager (Admin)
        admin_email = "admin@example.com"
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        admin_hashed = security.get_password_hash("admin123")

        if not admin_user:
            print("--- SEEDING: Creating HR Manager ---")
            db.add(models.User(
                name="HR Manager",
                email=admin_email,
                hashed_password=admin_hashed,
                position="HR Director",
                phone_number="099888777",
                role="admin"
            ))
        else:
            print("--- SEEDING: Updating HR Manager ---")
            admin_user.name = "HR Manager"
            admin_user.hashed_password = admin_hashed

        # 4. Seed or Update the Rest of the Team (Rith, Vith, Tra)
        team_members = [
            {"name": "Rith", "email": "rith@example.com", "position": "Developer"},
            {"name": "Vith", "email": "vith@example.com", "position": "Designer"},
            {"name": "Tra", "email": "tra@example.com", "position": "QA Engineer"}
        ]

        team_hashed_pass = security.get_password_hash("pass123")

        for member in team_members:
            existing_user = db.query(models.User).filter(models.User.email == member["email"]).first()

            if not existing_user:
                print(f"--- SEEDING: Creating {member['name']} ---")
                db.add(models.User(
                    name=member["name"],
                    email=member["email"],
                    hashed_password=team_hashed_pass,
                    position=member["position"],
                    phone_number="Not Provided",
                    role="employee"
                ))
            else:
                print(f"--- SEEDING: Updating existing user {member['name']} ---")
                existing_user.name = member["name"]
                existing_user.hashed_password = team_hashed_pass
                existing_user.position = member["position"]

        # Commit all new users and updates to the database
        db.commit()
        print("--- SEEDING COMPLETE: Database is ready ---")

    except Exception as e:
        print(f"--- SEEDING ERROR: {e} ---")
        db.rollback()
    finally:
        db.close()

    yield
    print("--- SYSTEM: Shutting Down ---")


# Create the FastAPI App instance
app = FastAPI(
    title="AttendEase API",
    description="Backend for Employee Attendance and Leave Management",
    lifespan=lifespan
)

# --- NEW: Serve Static Files for Profile Avatars ---
# 1. Create the folder if it doesn't exist so your app doesn't crash on startup
os.makedirs("static/avatars", exist_ok=True)

# 2. Tell FastAPI to make the 'static' folder accessible to the internet
app.mount("/static", StaticFiles(directory="static"), name="static")
# ---------------------------------------------------

# Include Routers
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "AttendEase API is running successfully!"}
