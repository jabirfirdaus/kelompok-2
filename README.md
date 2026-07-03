# Sistem Diagnosis Keluhan Kesehatan

Sistem konsultasi berbasis web yang menganalisis keluhan kesehatan pengguna menggunakan metode **Certainty Factor (CF)** untuk memberikan ranking kemungkinan penyakit beserta rekomendasi solusi.

> **Disclaimer:** Sistem ini adalah alat bantu edukasi dan triase awal, **bukan pengganti diagnosis medis profesional**.

## Fitur Utama

- Input keluhan dalam Bahasa Indonesia (teks bebas)
- Ekstraksi gejala otomatis (NLP keyword/fuzzy matching)
- Konfirmasi gejala oleh pengguna
- Ranking penyakit berdasarkan Certainty Factor
- Rekomendasi obat umum (OTC)
- Deteksi red flag / kondisi darurat
- Panel admin untuk kelola data

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Python + FastAPI |
| Database | MySQL + SQLAlchemy |
| Frontend | HTML / CSS / JavaScript |
| NLP | Sastrawi + RapidFuzz |

## Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/jabirfirdaus/kelompok-2.git
cd kelompok-2
```

### 2. Setup database MySQL
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p diagnosis_kesehatan < database/seed_data.sql
```

### 3. Setup backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 4. Konfigurasi environment
```bash
copy .env.example .env
# Edit .env sesuai konfigurasi MySQL lokal
```

### 5. Jalankan server
```bash
cd backend
python run.py
```

Server berjalan di `http://localhost:8000`
Dokumentasi API (Swagger): `http://localhost:8000/docs`

## Struktur Proyek

```
kelompok-2/
├── backend/           # API server (FastAPI)
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic validation
│   │   ├── routes/            # API endpoints
│   │   └── services/          # Business logic (CF, NLP, Red Flag)
│   ├── requirements.txt
│   └── run.py                 # Entry point
├── frontend/          # Antarmuka web
├── database/          # SQL schema & seed data
├── docs/              # Dokumentasi
└── tests/             # Unit tests
```

## Kelompok 2

| Anggota | Peran |
|---------|-------|
| Orang 1 | Data medis & basis pengetahuan |
| Orang 2 | Backend & database |
| Orang 3 | Modul NLP |
| Orang 4 | Frontend UI |
| Orang 5 | Testing & dokumentasi |