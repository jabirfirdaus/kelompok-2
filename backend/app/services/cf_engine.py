"""
Certainty Factor Engine
Menghitung tingkat kecocokan penyakit berdasarkan gejala yang dikonfirmasi user.

Rumus kombinasi CF:
    CF_kombinasi(CF1, CF2) = CF1 + CF2 × (1 - CF1)
    Dihitung berpasangan secara berurutan.
"""

from sqlalchemy.orm import Session
from app.models import GejalaPenyakit, Penyakit, PenyakitObat


def hitung_cf_kombinasi(cf_values: list[float]) -> float:
    """
    Menghitung CF gabungan dari beberapa gejala untuk satu penyakit.

    Contoh:
        cf_values = [0.6, 0.4]
        CF = 0.6 + 0.4 * (1 - 0.6) = 0.76
    """
    if not cf_values:
        return 0.0

    hasil = cf_values[0]
    for i in range(1, len(cf_values)):
        hasil = hasil + cf_values[i] * (1 - hasil)

    return round(hasil, 4)


def diagnosa(db: Session, gejala_ids: list[int]) -> list[dict]:
    """
    Proses utama diagnosis:
    1. Cari semua penyakit yang punya relasi dengan gejala yang dikonfirmasi
    2. Kumpulkan nilai CF per penyakit
    3. Hitung CF kombinasi
    4. Urutkan dari tertinggi ke terendah
    5. Sertakan data obat untuk setiap penyakit

    Args:
        db: SQLAlchemy session
        gejala_ids: list ID gejala yang sudah dikonfirmasi user

    Returns:
        List dict berisi ranking penyakit + persentase CF + obat
    """
    if not gejala_ids:
        return []

    # 1. Ambil semua relasi gejala-penyakit yang relevan
    relasi_list = (
        db.query(GejalaPenyakit)
        .filter(GejalaPenyakit.gejala_id.in_(gejala_ids))
        .all()
    )

    # 2. Kelompokkan CF per penyakit
    penyakit_cf_map: dict[int, list[float]] = {}
    for relasi in relasi_list:
        pid = relasi.penyakit_id
        if pid not in penyakit_cf_map:
            penyakit_cf_map[pid] = []
        penyakit_cf_map[pid].append(float(relasi.nilai_cf))

    # 3. Hitung CF kombinasi per penyakit
    hasil_ranking = []
    for penyakit_id, cf_values in penyakit_cf_map.items():
        cf_total = hitung_cf_kombinasi(cf_values)

        # Ambil data penyakit
        penyakit = db.query(Penyakit).get(penyakit_id)
        if not penyakit:
            continue

        # Ambil obat terkait
        obat_list = (
            db.query(PenyakitObat)
            .filter(PenyakitObat.penyakit_id == penyakit_id)
            .all()
        )

        obat_data = []
        for po in obat_list:
            if po.obat:
                obat_data.append(po.obat.to_dict())

        hasil_ranking.append({
            "penyakit_id": penyakit.id,
            "nama_penyakit": penyakit.nama_penyakit,
            "persentase_cf": round(cf_total * 100, 2),
            "tingkat_urgensi": penyakit.tingkat_urgensi,
            "deskripsi": penyakit.deskripsi,
            "obat": obat_data,
            "sumber_referensi": penyakit.sumber_referensi,
        })

    # 4. Urutkan dari persentase tertinggi
    hasil_ranking.sort(key=lambda x: x["persentase_cf"], reverse=True)

    return hasil_ranking
