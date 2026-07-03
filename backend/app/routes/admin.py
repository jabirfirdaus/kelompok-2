"""
Routes: Admin — CRUD gejala, penyakit, obat, dan relasi.
Untuk panel admin internal (bukan pengguna umum).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Gejala, Penyakit, Obat, KategoriGejala,
    GejalaPenyakit, PenyakitObat,
)
from app.schemas import (
    GejalaCreate, GejalaUpdate,
    PenyakitCreate, PenyakitUpdate,
    ObatCreate, ObatUpdate,
    GejalaPenyakitCreate,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============================================
# CRUD Gejala
# ============================================
@router.get("/gejala")
def admin_list_gejala(db: Session = Depends(get_db)):
    return [g.to_dict() for g in db.query(Gejala).all()]


@router.post("/gejala")
def admin_create_gejala(data: GejalaCreate, db: Session = Depends(get_db)):
    existing = db.query(Gejala).filter(Gejala.kode_gejala == data.kode_gejala).first()
    if existing:
        raise HTTPException(400, f"Kode gejala '{data.kode_gejala}' sudah ada")

    gejala = Gejala(**data.model_dump())
    db.add(gejala)
    db.commit()
    db.refresh(gejala)
    return {"message": "Gejala berhasil ditambahkan", "data": gejala.to_dict()}


@router.put("/gejala/{gejala_id}")
def admin_update_gejala(gejala_id: int, data: GejalaUpdate, db: Session = Depends(get_db)):
    gejala = db.query(Gejala).get(gejala_id)
    if not gejala:
        raise HTTPException(404, "Gejala tidak ditemukan")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(gejala, key, value)

    db.commit()
    db.refresh(gejala)
    return {"message": "Gejala berhasil diupdate", "data": gejala.to_dict()}


@router.delete("/gejala/{gejala_id}")
def admin_delete_gejala(gejala_id: int, db: Session = Depends(get_db)):
    gejala = db.query(Gejala).get(gejala_id)
    if not gejala:
        raise HTTPException(404, "Gejala tidak ditemukan")

    db.delete(gejala)
    db.commit()
    return {"message": f"Gejala '{gejala.nama_gejala}' berhasil dihapus"}


# ============================================
# CRUD Penyakit
# ============================================
@router.get("/penyakit")
def admin_list_penyakit(db: Session = Depends(get_db)):
    return [p.to_dict() for p in db.query(Penyakit).all()]


@router.post("/penyakit")
def admin_create_penyakit(data: PenyakitCreate, db: Session = Depends(get_db)):
    existing = db.query(Penyakit).filter(Penyakit.kode_penyakit == data.kode_penyakit).first()
    if existing:
        raise HTTPException(400, f"Kode penyakit '{data.kode_penyakit}' sudah ada")

    penyakit = Penyakit(**data.model_dump())
    db.add(penyakit)
    db.commit()
    db.refresh(penyakit)
    return {"message": "Penyakit berhasil ditambahkan", "data": penyakit.to_dict()}


@router.put("/penyakit/{penyakit_id}")
def admin_update_penyakit(penyakit_id: int, data: PenyakitUpdate, db: Session = Depends(get_db)):
    penyakit = db.query(Penyakit).get(penyakit_id)
    if not penyakit:
        raise HTTPException(404, "Penyakit tidak ditemukan")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(penyakit, key, value)

    db.commit()
    db.refresh(penyakit)
    return {"message": "Penyakit berhasil diupdate", "data": penyakit.to_dict()}


@router.delete("/penyakit/{penyakit_id}")
def admin_delete_penyakit(penyakit_id: int, db: Session = Depends(get_db)):
    penyakit = db.query(Penyakit).get(penyakit_id)
    if not penyakit:
        raise HTTPException(404, "Penyakit tidak ditemukan")

    db.delete(penyakit)
    db.commit()
    return {"message": f"Penyakit '{penyakit.nama_penyakit}' berhasil dihapus"}


# ============================================
# CRUD Obat
# ============================================
@router.get("/obat")
def admin_list_obat(db: Session = Depends(get_db)):
    return [o.to_dict() for o in db.query(Obat).all()]


@router.post("/obat")
def admin_create_obat(data: ObatCreate, db: Session = Depends(get_db)):
    obat = Obat(**data.model_dump())
    db.add(obat)
    db.commit()
    db.refresh(obat)
    return {"message": "Obat berhasil ditambahkan", "data": obat.to_dict()}


@router.put("/obat/{obat_id}")
def admin_update_obat(obat_id: int, data: ObatUpdate, db: Session = Depends(get_db)):
    obat = db.query(Obat).get(obat_id)
    if not obat:
        raise HTTPException(404, "Obat tidak ditemukan")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obat, key, value)

    db.commit()
    db.refresh(obat)
    return {"message": "Obat berhasil diupdate", "data": obat.to_dict()}


@router.delete("/obat/{obat_id}")
def admin_delete_obat(obat_id: int, db: Session = Depends(get_db)):
    obat = db.query(Obat).get(obat_id)
    if not obat:
        raise HTTPException(404, "Obat tidak ditemukan")

    db.delete(obat)
    db.commit()
    return {"message": f"Obat '{obat.nama_obat}' berhasil dihapus"}


# ============================================
# Relasi Gejala-Penyakit (CF)
# ============================================
@router.get("/relasi-cf")
def admin_list_relasi_cf(db: Session = Depends(get_db)):
    return [gp.to_dict() for gp in db.query(GejalaPenyakit).all()]


@router.post("/relasi-cf")
def admin_create_relasi_cf(data: GejalaPenyakitCreate, db: Session = Depends(get_db)):
    # Validasi gejala & penyakit ada
    if not db.query(Gejala).get(data.gejala_id):
        raise HTTPException(404, "Gejala tidak ditemukan")
    if not db.query(Penyakit).get(data.penyakit_id):
        raise HTTPException(404, "Penyakit tidak ditemukan")

    # Cek duplikat
    existing = (
        db.query(GejalaPenyakit)
        .filter(
            GejalaPenyakit.gejala_id == data.gejala_id,
            GejalaPenyakit.penyakit_id == data.penyakit_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "Relasi gejala-penyakit sudah ada")

    relasi = GejalaPenyakit(**data.model_dump())
    db.add(relasi)
    db.commit()
    db.refresh(relasi)
    return {"message": "Relasi CF berhasil ditambahkan", "data": relasi.to_dict()}


@router.delete("/relasi-cf/{relasi_id}")
def admin_delete_relasi_cf(relasi_id: int, db: Session = Depends(get_db)):
    relasi = db.query(GejalaPenyakit).get(relasi_id)
    if not relasi:
        raise HTTPException(404, "Relasi tidak ditemukan")

    db.delete(relasi)
    db.commit()
    return {"message": "Relasi CF berhasil dihapus"}


# ============================================
# Kategori Gejala
# ============================================
@router.get("/kategori")
def admin_list_kategori(db: Session = Depends(get_db)):
    return [k.to_dict() for k in db.query(KategoriGejala).all()]


@router.post("/kategori")
def admin_create_kategori(nama_kategori: str, db: Session = Depends(get_db)):
    kategori = KategoriGejala(nama_kategori=nama_kategori)
    db.add(kategori)
    db.commit()
    db.refresh(kategori)
    return {"message": "Kategori berhasil ditambahkan", "data": kategori.to_dict()}
