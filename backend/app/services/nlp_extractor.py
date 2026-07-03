"""
NLP Extractor — Modul Ekstraksi Gejala dari Teks Bebas
Placeholder untuk Orang 3 (NLP).

Saat ini menggunakan Opsi A: keyword matching + fuzzy matching.
Orang 3 akan mengembangkan modul ini lebih lanjut.
"""

from rapidfuzz import fuzz, process


# Kamus sinonim — Orang 3 akan melengkapi ini
SINONIM_GEJALA: dict[str, str] = {
    "sakit kepala": "pusing",
    "kepala pusing": "pusing",
    "cephalgia": "pusing",
    "mules": "nyeri perut",
    "sakit perut": "nyeri perut",
    "perut sakit": "nyeri perut",
    "muntaber": "muntah",
    "meriang": "demam",
    "badan panas": "demam",
    "pilek": "hidung tersumbat",
    "ingus": "hidung tersumbat",
    "batuk-batuk": "batuk",
    "seseg": "sesak napas",
    "ngos-ngosan": "sesak napas",
    "lemes": "lemas",
    "tidak bertenaga": "lemas",
    "capek": "lemas",
    "kelelahan": "lemas",
    "eneg": "mual",
    "pengen muntah": "mual",
}


def extract_symptoms(
    user_text: str,
    known_symptoms: list[dict],
    threshold: int = 70,
) -> list[dict]:
    """
    Ekstrak gejala dari teks bebas pengguna.

    Args:
        user_text: teks keluhan dari pengguna
        known_symptoms: list dict {'id': int, 'nama_gejala': str} dari database
        threshold: skor minimum fuzzy matching (0-100)

    Returns:
        List dict: [{"gejala_id": 1, "nama_gejala": "mual", "confidence": 0.95}]
    """
    text_lower = user_text.lower().strip()

    # 1. Ganti sinonim yang dikenal
    for sinonim, gejala_baku in SINONIM_GEJALA.items():
        if sinonim in text_lower:
            text_lower = text_lower.replace(sinonim, gejala_baku)

    # 2. Buat mapping nama → data gejala
    nama_to_gejala = {g["nama_gejala"].lower(): g for g in known_symptoms}
    nama_list = list(nama_to_gejala.keys())

    # 3. Cek exact match dulu
    matched = []
    matched_ids = set()

    for nama in nama_list:
        if nama in text_lower:
            gejala = nama_to_gejala[nama]
            if gejala["id"] not in matched_ids:
                matched.append({
                    "gejala_id": gejala["id"],
                    "nama_gejala": gejala["nama_gejala"],
                    "confidence": 0.95,
                })
                matched_ids.add(gejala["id"])

    # 4. Fuzzy match untuk kata-kata yang belum ter-match
    words = text_lower.split()
    for i in range(len(words)):
        # Coba 1-kata dan 2-kata (bigram)
        candidates = [words[i]]
        if i + 1 < len(words):
            candidates.append(f"{words[i]} {words[i+1]}")

        for candidate in candidates:
            result = process.extractOne(
                candidate,
                nama_list,
                scorer=fuzz.partial_ratio,
                score_cutoff=threshold,
            )
            if result:
                best_match, score, _ = result
                gejala = nama_to_gejala[best_match]
                if gejala["id"] not in matched_ids:
                    matched.append({
                        "gejala_id": gejala["id"],
                        "nama_gejala": gejala["nama_gejala"],
                        "confidence": round(score / 100, 2),
                    })
                    matched_ids.add(gejala["id"])

    # 5. Urutkan berdasarkan confidence tertinggi
    matched.sort(key=lambda x: x["confidence"], reverse=True)

    return matched
