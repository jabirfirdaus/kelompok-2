"""
SQLAlchemy Models — Sistem Diagnosis Keluhan Kesehatan
Mapping dari tabel MySQL ke Python class.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Enum, DECIMAL,
    ForeignKey, TIMESTAMP, JSON, func
)
from sqlalchemy.orm import relationship

from app.database import Base


# ============================================
# 1. Kategori Gejala
# ============================================
class KategoriGejala(Base):
    __tablename__ = "kategori_gejala"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nama_kategori = Column(String(100), nullable=False)

    # Relasi
    gejala_list = relationship("Gejala", back_populates="kategori")

    def to_dict(self):
        return {
            "id": self.id,
            "nama_kategori": self.nama_kategori,
        }


# ============================================
# 2. Gejala
# ============================================
class Gejala(Base):
    __tablename__ = "gejala"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kode_gejala = Column(String(10), unique=True, nullable=False)
    nama_gejala = Column(String(150), nullable=False)
    kategori_id = Column(Integer, ForeignKey("kategori_gejala.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    kategori = relationship("KategoriGejala", back_populates="gejala_list")
    penyakit_relasi = relationship("GejalaPenyakit", back_populates="gejala")

    def to_dict(self):
        return {
            "id": self.id,
            "kode_gejala": self.kode_gejala,
            "nama_gejala": self.nama_gejala,
            "kategori": self.kategori.nama_kategori if self.kategori else None,
        }


# ============================================
# 3. Penyakit
# ============================================
class Penyakit(Base):
    __tablename__ = "penyakit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kode_penyakit = Column(String(10), unique=True, nullable=False)
    nama_penyakit = Column(String(150), nullable=False)
    deskripsi = Column(Text)
    tingkat_urgensi = Column(
        Enum("mandiri", "apotek", "fasilitas_kesehatan", "darurat"),
        nullable=False
    )
    sumber_referensi = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    gejala_relasi = relationship("GejalaPenyakit", back_populates="penyakit")
    obat_relasi = relationship("PenyakitObat", back_populates="penyakit")

    def to_dict(self):
        return {
            "id": self.id,
            "kode_penyakit": self.kode_penyakit,
            "nama_penyakit": self.nama_penyakit,
            "deskripsi": self.deskripsi,
            "tingkat_urgensi": self.tingkat_urgensi,
            "sumber_referensi": self.sumber_referensi,
        }


# ============================================
# 4. Obat
# ============================================
class Obat(Base):
    __tablename__ = "obat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nama_obat = Column(String(150), nullable=False)
    jenis = Column(Enum("bebas", "bebas_terbatas"), nullable=False)
    catatan_penggunaan = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    penyakit_relasi = relationship("PenyakitObat", back_populates="obat")

    def to_dict(self):
        return {
            "id": self.id,
            "nama_obat": self.nama_obat,
            "jenis": self.jenis,
            "catatan_penggunaan": self.catatan_penggunaan,
        }


# ============================================
# 5. Relasi Gejala ↔ Penyakit (CF)
# ============================================
class GejalaPenyakit(Base):
    __tablename__ = "gejala_penyakit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gejala_id = Column(Integer, ForeignKey("gejala.id", ondelete="CASCADE"), nullable=False)
    penyakit_id = Column(Integer, ForeignKey("penyakit.id", ondelete="CASCADE"), nullable=False)
    nilai_cf = Column(DECIMAL(3, 2), nullable=False)

    # Relasi
    gejala = relationship("Gejala", back_populates="penyakit_relasi")
    penyakit = relationship("Penyakit", back_populates="gejala_relasi")

    def to_dict(self):
        return {
            "id": self.id,
            "gejala_id": self.gejala_id,
            "penyakit_id": self.penyakit_id,
            "nama_gejala": self.gejala.nama_gejala if self.gejala else None,
            "nama_penyakit": self.penyakit.nama_penyakit if self.penyakit else None,
            "nilai_cf": float(self.nilai_cf),
        }


# ============================================
# 6. Relasi Penyakit ↔ Obat
# ============================================
class PenyakitObat(Base):
    __tablename__ = "penyakit_obat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    penyakit_id = Column(Integer, ForeignKey("penyakit.id", ondelete="CASCADE"), nullable=False)
    obat_id = Column(Integer, ForeignKey("obat.id", ondelete="CASCADE"), nullable=False)

    # Relasi
    penyakit = relationship("Penyakit", back_populates="obat_relasi")
    obat = relationship("Obat", back_populates="penyakit_relasi")


# ============================================
# 7. Red Flag
# ============================================
class RedFlag(Base):
    __tablename__ = "red_flag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nama_kondisi = Column(String(150), nullable=False)
    pesan_peringatan = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relasi
    gejala_list = relationship("RedFlagGejala", back_populates="red_flag")

    def to_dict(self):
        return {
            "id": self.id,
            "nama_kondisi": self.nama_kondisi,
            "pesan_peringatan": self.pesan_peringatan,
            "gejala": [rfg.gejala.nama_gejala for rfg in self.gejala_list if rfg.gejala],
        }


class RedFlagGejala(Base):
    __tablename__ = "red_flag_gejala"

    id = Column(Integer, primary_key=True, autoincrement=True)
    red_flag_id = Column(Integer, ForeignKey("red_flag.id", ondelete="CASCADE"), nullable=False)
    gejala_id = Column(Integer, ForeignKey("gejala.id", ondelete="CASCADE"), nullable=False)

    # Relasi
    red_flag = relationship("RedFlag", back_populates="gejala_list")
    gejala = relationship("Gejala")


# ============================================
# 8. Riwayat Konsultasi
# ============================================
class RiwayatKonsultasi(Base):
    __tablename__ = "riwayat_konsultasi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False)
    gejala_input = Column(Text)
    gejala_terkonfirmasi = Column(JSON)
    hasil_ranking = Column(JSON)
    red_flag_terdeteksi = Column(JSON)
    dibuat_pada = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "gejala_input": self.gejala_input,
            "gejala_terkonfirmasi": self.gejala_terkonfirmasi,
            "hasil_ranking": self.hasil_ranking,
            "red_flag_terdeteksi": self.red_flag_terdeteksi,
            "dibuat_pada": str(self.dibuat_pada),
        }
