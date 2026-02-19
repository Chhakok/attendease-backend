from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import models, database, security
from .routers import auth, attendance, leave,history



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Tables
    print("--- SYSTEM: Booting Up and Creating Tables ---")
    models.Base.metadata.create_all(bind=database.engine)

    db = database.SessionLocal()
    try:
        # 2. Seed Test Employee
        test_user = db.query(models.User).filter(models.User.email == "test@example.com").first()
        if not test_user:
            print("--- SEEDING: Creating Test Employee ---")
            db.add(models.User(
                name="Heng Sovann",
                email="test@example.com",
                hashed_password=security.get_password_hash("password123"),
                position="Senior Flutter Dev",
                phone_number="+855 12 999 888",
                role="employee"
            ))
            db.commit()

        # 3. Seed HR Manager (Admin)
        admin_user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
        if not admin_user:
            print("--- SEEDING: Creating HR Manager ---")
            db.add(models.User(
                name="HR Manager",
                email="admin@example.com",
                hashed_password=security.get_password_hash("admin123"),
                position="HR Director",
                phone_number="099888777",
                role="admin"
            ))
            db.commit()
            print("--- SEEDING COMPLETE: Database is ready ---")
        else:
            print("--- SYSTEM: Users already exist in database ---")

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

# Include Routers
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "AttendEase API is running successfully!"}

