"""
Routes: Konsultasi — endpoint utama untuk diagnosis kesehatan.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Gejala
from app.schemas import (
    EkstrakGejalaRequest,
    EkstrakGejalaResponse,
    GejalaTerdeteksi,
    DiagnosisRequest,
    DiagnosisResponse,
    HasilPenyakit,
    RedFlagAlert,
    ObatResponse,
)
from app.services.cf_engine import diagnosa
from app.services.red_flag import cek_red_flags
from app.services.nlp_extractor import extract_symptoms

router = APIRouter(prefix="/api", tags=["Konsultasi"])


@router.post("/ekstrak-gejala", response_model=EkstrakGejalaResponse)
def ekstrak_gejala(req: EkstrakGejalaRequest, db: Session = Depends(get_db)):
    """
    Langkah 1: Terima teks keluhan → ekstrak gejala otomatis.
    User akan mengkonfirmasi hasilnya sebelum lanjut ke diagnosis.
    """
    # Ambil semua gejala dari DB
    semua_gejala = db.query(Gejala).all()
    known = [{"id": g.id, "nama_gejala": g.nama_gejala} for g in semua_gejala]

    # Ekstrak gejala dari teks
    hasil = extract_symptoms(req.teks, known)

    return EkstrakGejalaResponse(
        gejala_terdeteksi=[
            GejalaTerdeteksi(
                gejala_id=h["gejala_id"],
                nama_gejala=h["nama_gejala"],
                confidence=h["confidence"],
            )
            for h in hasil
        ],
        teks_asli=req.teks,
    )


@router.post("/diagnosis", response_model=DiagnosisResponse)
def diagnosis(req: DiagnosisRequest, db: Session = Depends(get_db)):
    """
    Langkah 2: Terima gejala yang sudah dikonfirmasi user → hitung CF → ranking.
    """
    # Validasi: pastikan gejala_ids valid
    valid_ids = []
    for gid in req.gejala_ids:
        gejala = db.query(Gejala).get(gid)
        if gejala:
            valid_ids.append(gid)

    if not valid_ids:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada gejala valid yang ditemukan. Pastikan ID gejala benar."
        )

    # Hitung ranking CF
    ranking_data = diagnosa(db, valid_ids)

    # Cek red flag
    red_flag_data = cek_red_flags(db, valid_ids)

    # Format response
    ranking = [
        HasilPenyakit(
            penyakit_id=r["penyakit_id"],
            nama_penyakit=r["nama_penyakit"],
            persentase_cf=r["persentase_cf"],
            tingkat_urgensi=r["tingkat_urgensi"],
            deskripsi=r["deskripsi"],
            obat=[ObatResponse(**o) for o in r["obat"]],
            sumber_referensi=r["sumber_referensi"],
        )
        for r in ranking_data
    ]

    red_flags = [
        RedFlagAlert(
            nama_kondisi=rf["nama_kondisi"],
            pesan_peringatan=rf["pesan_peringatan"],
            gejala_terkait=rf["gejala_terkait"],
        )
        for rf in red_flag_data
    ]

    return DiagnosisResponse(ranking=ranking, red_flags=red_flags)


@router.get("/gejala", response_model=list[dict])
def list_gejala(db: Session = Depends(get_db)):
    """Ambil semua gejala — untuk frontend dropdown/autocomplete."""
    gejala_list = db.query(Gejala).all()
    return [g.to_dict() for g in gejala_list]
