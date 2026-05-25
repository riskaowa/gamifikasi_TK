"""
Script untuk query database langsung dan mencari soal bermasalah
Menggunakan SQLite untuk analisis mendalam
"""

import sqlite3
import sys
import os

project_root = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main')
db_path = os.path.join(project_root, 'app.db')

if not os.path.exists(db_path):
    print(f"Database tidak ditemukan di {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query untuk melihat struktur soal huruf
cursor.execute("""
    SELECT id, pertanyaan, pilihan_a, pilihan_b, pilihan_c, pilihan_d, jawaban_benar
    FROM soal
    WHERE kategori = 'huruf'
    ORDER BY id
    LIMIT 50
""")

rows = cursor.fetchall()

print("SOAL HURUF - 50 PERTAMA")
print("="*100)

for row in rows:
    id_soal = row[0]
    pertanyaan = row[1] or ""
    opt_a = row[2] or ""
    opt_b = row[3] or ""
    opt_c = row[4] or ""
    opt_d = row[5] or ""
    jawaban_benar = row[6] or ""
    
    # Map jawaban ke opsi
    jawaban_map = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
    # Handle normalized form
    if jawaban_benar.lower().startswith('option_'):
        letter = jawaban_benar.replace('option_', '').upper()
    else:
        letter = jawaban_benar.upper()
    
    answer_text = jawaban_map.get(letter if letter in jawaban_map else 'A', "")
    
    print(f"\nID {id_soal:3d} | Q: {pertanyaan[:40]:40s} | Ans: {letter} = {answer_text[:10]:10s}")
    print(f"        Opsi: A={opt_a[:8]:8s}, B={opt_b[:8]:8s}, C={opt_c[:8]:8s}, D={opt_d[:8]:8s}")

conn.close()
