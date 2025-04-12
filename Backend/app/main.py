from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from app.routes import medical_record, patient, doctor, appointment, auth

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                 "https://healthcare-appointment-scheduling-system.vercel.app"
                   ],  # Your React app's URL
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

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(content={"message": "CORS preflight"}, status_code=200)

@app.get("/")
def read_root():
    return {"message": "Hospital API - Go to /docs for documentation"}