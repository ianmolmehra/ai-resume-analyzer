import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time

from config import settings
from database import init_db
from routers import resume as resume_router
from routers import matching as matching_router
from routers import analytics as analytics_router
from routers import admin as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/resumes", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/reports", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/jd", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"DB init warning (may already exist): {e}")

    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## AI Resume Analyzer & Job Matching Platform

A production-grade platform that:
- 📄 Parses resumes (PDF/DOCX) and extracts structured information
- 🧠 Performs intelligent skill extraction with confidence scoring  
- 🎯 Matches resumes against job descriptions
- 📊 Generates detailed match reports with skill gap analysis
- 📈 Provides analytics dashboard and candidate rankings
- 📑 Exports downloadable PDF reports
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})


# Static files for uploads (optional)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(resume_router.router, prefix="/api/v1")
app.include_router(matching_router.router, prefix="/api/v1")
app.include_router(analytics_router.router, prefix="/api/v1")
app.include_router(admin_router.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
