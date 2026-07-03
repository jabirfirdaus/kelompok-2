"""
Red Flag Detector
Mendeteksi kombinasi gejala yang mengindikasikan kondisi darurat.
Jika terdeteksi, sistem menampilkan peringatan prioritas utama.
"""

from sqlalchemy.orm import Session
from app.models import RedFlag, RedFlagGejala


def cek_red_flags(db: Session, gejala_ids: list[int]) -> list[dict]:
    """
    Periksa apakah kombinasi gejala user termasuk red flag.

    Logika:
    - Ambil semua red flag dari database
    - Untuk setiap red flag, cek apakah SEMUA gejala yang diperlukan
      ada dalam gejala_ids user
    - Jika ya, masukkan ke daftar peringatan

    Args:
        db: SQLAlchemy session
        gejala_ids: list ID gejala yang dikonfirmasi user

    Returns:
        List dict berisi red flag yang terdeteksi
    """
    if not gejala_ids:
        return []

    gejala_set = set(gejala_ids)
    alerts = []

    # Ambil semua red flag beserta gejala terkait
    all_red_flags = db.query(RedFlag).all()

    for rf in all_red_flags:
        # Ambil gejala yang dibutuhkan untuk red flag ini
        rf_gejala_ids = {rfg.gejala_id for rfg in rf.gejala_list}

        # Cek apakah SEMUA gejala red flag ada dalam gejala user
        if rf_gejala_ids and rf_gejala_ids.issubset(gejala_set):
            alerts.append({
                "nama_kondisi": rf.nama_kondisi,
                "pesan_peringatan": rf.pesan_peringatan,
                "gejala_terkait": [
                    rfg.gejala.nama_gejala
                    for rfg in rf.gejala_list
                    if rfg.gejala
                ],
            })

    return alerts
