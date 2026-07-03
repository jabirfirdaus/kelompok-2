"""
Entry point — jalankan dengan: python run.py
Server akan berjalan di http://localhost:8000
Dokumentasi API otomatis di http://localhost:8000/docs (Swagger UI)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import Base, engine
from app.routes.konsultasi import router as konsultasi_router
from app.routes.admin import router as admin_router

# Buat semua tabel jika belum ada
Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI(
    title="Sistem Diagnosis Keluhan Kesehatan",
    description=(
        "API untuk konsultasi kesehatan berbasis Certainty Factor. "
        "Sistem ini adalah alat bantu edukasi, bukan pengganti diagnosis dokter."
    ),
    version="1.0.0",
)

# CORS — izinkan frontend akses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk development, nanti bisa di-restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="frontend")

# Register routers
app.include_router(konsultasi_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "nama": "Sistem Diagnosis Keluhan Kesehatan",
        "versi": "1.0.0",
        "kelompok": "Kelompok 2",
        "docs": "/docs",
        "disclaimer": (
            "Sistem ini adalah alat bantu edukasi dan triase awal, "
            "bukan pengganti diagnosis medis profesional."
        ),
    }


if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
