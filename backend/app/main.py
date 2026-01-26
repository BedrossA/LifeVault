"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import logger
from app.db.base import init_db
from app.db.mongodb import connect_mongodb, close_mongodb
from app.db.redis import connect_redis, close_redis
from app.api.v1.endpoints import auth, face, analytics, intelligence, goal_milestones
from app.middleware.cors_options import AuthCorsOptionsMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    
    # Initialize databases
    try:
        init_db()
        logger.info("PostgreSQL initialized")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
    
    try:
        await connect_mongodb()
        logger.info("MongoDB connected")
    except Exception as e:
        logger.error(f"Failed to connect MongoDB: {e}")
    
    try:
        await connect_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Failed to connect Redis: {e}")
    
    logger.info("All databases connected successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_mongodb()
    await close_redis()
    logger.info("Databases closed")

# Define OpenAPI Tags for better documentation organization
tags_metadata = [
    {"name": "Authentication", "description": "User authentication and JWT management"},
    {"name": "Face Recognition", "description": "Biometric enrollment and verification"},
    {"name": "Analytics", "description": "Personal data insights and tracking"},
    {"name": "Intelligence", "description": "AI-powered analytics: correlations, anomalies, patterns, predictions"},
    {"name": "Goals", "description": "Goal tracking with milestones"},
]

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LifeVault - Encrypted Personal Analytics Platform with Face Recognition",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthCorsOptionsMiddleware)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
    )
app.include_router(
    face.router,
    prefix=f"{settings.API_V1_PREFIX}/face",
    tags=["Face Recognition"]
    )
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"]
)
app.include_router(
    intelligence.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence",
    tags=["Intelligence"]
)
app.include_router(
    goal_milestones.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Goals"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "databases": {
            "postgresql": "connected",
            "mongodb": "connected",
            "redis": "connected"
        }
    }

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )
