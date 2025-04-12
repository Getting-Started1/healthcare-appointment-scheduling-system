from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes import medical_record, patient, doctor, appointment, auth

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(doctor.router)
app.include_router(appointment.router)
app.include_router(medical_record.router)

# Database setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={
        "models": [
            "app.models.user",
            "app.models.patient",
            "app.models.doctor",
            "app.models.appointment",
            "app.models.medical_record"
        ]
    },
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
def read_root():
    return {"message": "Hospital API - Go to /docs for documentation"}