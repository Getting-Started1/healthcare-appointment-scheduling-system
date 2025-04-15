from fastapi import FastAPI, Request, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.routes import medical_record, patient, doctor, appointment, auth

# Create FastAPI app with metadata
app = FastAPI(
    title="Healthcare Appointment System API",
    description="""
    A comprehensive API for managing healthcare appointments, patient records, and doctor schedules.
    
    ## Features
    * User Authentication and Authorization
    * Patient Management
    * Doctor Management
    * Appointment Scheduling
    * Medical Records Management
    
    ## Authentication
    All endpoints except registration and login require a valid JWT token.
    Include the token in the Authorization header: `Bearer <token>`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                 "https://healthcare-appointment-scheduling-system.vercel.app",
                 "http://localhost:5173",  # Vite default port
                 "http://127.0.0.1:5173",  # Vite default port
                 "http://localhost:8000",  # Your backend
                 "http://127.0.0.1:8000"   # Your backend
                   ],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with tags
app.include_router(auth.router, tags=["Authentication"])
app.include_router(patient.router, tags=["Patients"])
app.include_router(doctor.router, tags=["Doctors"])
app.include_router(appointment.router, tags=["Appointments"])
app.include_router(medical_record.router, tags=["Medical Records"])

# Database configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare_db")

DATABASE_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database setup
register_tortoise(
    app,
    db_url=DATABASE_URL,
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

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Healthcare Appointment System API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPError"
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "ServerError"
            }
        }
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Check the health status of the API.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: API information
    """
    return {
        "name": "Healthcare Appointment System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(content={"message": "CORS preflight"}, status_code=200)