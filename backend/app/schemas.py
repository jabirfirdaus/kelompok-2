"""
Pydantic Schemas — request/response validation untuk API.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ============================================
# Gejala
# ============================================
class GejalaCreate(BaseModel):
    kode_gejala: str = Field(..., max_length=10, examples=["G01"])
    nama_gejala: str = Field(..., max_length=150, examples=["mual"])
    kategori_id: Optional[int] = None


class GejalaUpdate(BaseModel):
    nama_gejala: Optional[str] = Field(None, max_length=150)
    kategori_id: Optional[int] = None


class GejalaResponse(BaseModel):
    id: int
    kode_gejala: str
    nama_gejala: str
    kategori: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# Penyakit
# ============================================
class PenyakitCreate(BaseModel):
    kode_penyakit: str = Field(..., max_length=10, examples=["P01"])
    nama_penyakit: str = Field(..., max_length=150, examples=["Gastritis"])
    deskripsi: Optional[str] = None
    tingkat_urgensi: str = Field(..., examples=["apotek"])
    sumber_referensi: Optional[str] = None


class PenyakitUpdate(BaseModel):
    nama_penyakit: Optional[str] = Field(None, max_length=150)
    deskripsi: Optional[str] = None
    tingkat_urgensi: Optional[str] = None
    sumber_referensi: Optional[str] = None


class PenyakitResponse(BaseModel):
    id: int
    kode_penyakit: str
    nama_penyakit: str
    deskripsi: Optional[str] = None
    tingkat_urgensi: str
    sumber_referensi: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# Obat
# ============================================
class ObatCreate(BaseModel):
    nama_obat: str = Field(..., max_length=150, examples=["Antasida"])
    jenis: str = Field(..., examples=["bebas"])
    catatan_penggunaan: Optional[str] = None


class ObatUpdate(BaseModel):
    nama_obat: Optional[str] = Field(None, max_length=150)
    jenis: Optional[str] = None
    catatan_penggunaan: Optional[str] = None


class ObatResponse(BaseModel):
    id: int
    nama_obat: str
    jenis: str
    catatan_penggunaan: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# Relasi Gejala-Penyakit
# ============================================
class GejalaPenyakitCreate(BaseModel):
    gejala_id: int
    penyakit_id: int
    nilai_cf: float = Field(..., ge=0.0, le=1.0, examples=[0.6])


# ============================================
# Konsultasi — Request & Response
# ============================================
class EkstrakGejalaRequest(BaseModel):
    teks: str = Field(
        ...,
        min_length=3,
        examples=["perut saya mual dan pusing sejak semalam"]
    )


class GejalaTerdeteksi(BaseModel):
    gejala_id: int
    nama_gejala: str
    confidence: float


class EkstrakGejalaResponse(BaseModel):
    gejala_terdeteksi: list[GejalaTerdeteksi]
    teks_asli: str


class DiagnosisRequest(BaseModel):
    gejala_ids: list[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 5, 12]]
    )


class HasilPenyakit(BaseModel):
    penyakit_id: int
    nama_penyakit: str
    persentase_cf: float
    tingkat_urgensi: str
    deskripsi: Optional[str] = None
    obat: list[ObatResponse] = []
    sumber_referensi: Optional[str] = None


class RedFlagAlert(BaseModel):
    nama_kondisi: str
    pesan_peringatan: str
    gejala_terkait: list[str]


class DiagnosisResponse(BaseModel):
    ranking: list[HasilPenyakit]
    red_flags: list[RedFlagAlert] = []
    disclaimer: str = (
        "PERINGATAN: Ini bukan diagnosis medis resmi. Hasil ini hanya bersifat edukatif "
        "dan sebagai triase awal. Jika gejala memburuk atau berlangsung lebih "
        "dari 3 hari, segera periksakan diri ke dokter atau fasilitas kesehatan terdekat."
    )
