"""
Script untuk mencari soal huruf spesifik: V, N, Y, R, G, E
dan menganalisis apakah jawaban benar
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

# Query untuk semua soal huruf
cursor.execute("""
    SELECT id, pertanyaan, pilihan_a, pilihan_b, pilihan_c, pilihan_d, jawaban_benar
    FROM soal
    WHERE kategori = 'huruf'
    ORDER BY id
""")

rows = cursor.fetchall()

print("ANALISIS SOAL HURUF - MENCARI MASALAH")
print("="*120)

target_huruf = ['V', 'N', 'Y', 'R', 'G', 'E', 'F']
problematic = []

for row in rows:
    id_soal = row[0]
    pertanyaan = row[1] or ""
    opt_a = row[2] or ""
    opt_b = row[3] or ""
    opt_c = row[4] or ""
    opt_d = row[5] or ""
    jawaban_benar = row[6] or ""
    
    # Check if ini soal tentang huruf target
    is_target = False
    for huruf in target_huruf:
        if huruf.lower() in pertanyaan.lower() or huruf in opt_a or huruf in opt_b or huruf in opt_c or huruf in opt_d:
            is_target = True
            break
    
    if is_target:
        # Map jawaban ke opsi
        letter = jawaban_benar.upper() if not jawaban_benar.startswith('option_') else jawaban_benar.replace('option_', '').upper()
        jawaban_map = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
        answer_text = jawaban_map.get(letter if letter in jawaban_map else 'A', "")
        
        # Untuk soal "Huruf apa ini?" atau "Pasangan huruf besar dari" 
        # jawaban harus berupa single huruf dari A-Z
        if "Huruf apa ini" in pertanyaan or "Pasangan huruf besar" in pertanyaan:
            # Extract expected answer dari options
            # Salah satu dari opsi harus match dengan huruf yang ditanyakan
            if len(answer_text) == 1 and answer_text.isalpha():
                # Validasi: jawaban harus ada di dalam opsi-opsi pilihan
                # Dan harus berupa huruf tunggal
                pass
        
        # Untuk soal "Setelah huruf X adalah" atau "Sebelum huruf X adalah"
        if "Setelah huruf" in pertanyaan or "Sebelum huruf" in pertanyaan:
            # Extract huruf target dari pertanyaan
            import re
            match = re.search(r'huruf\s+([A-Za-z])', pertanyaan)
            if match:
                target_letter = match.group(1).upper()
                expected = None
                
                if "Setelah" in pertanyaan:
                    expected = chr(ord(target_letter) + 1)
                elif "Sebelum" in pertanyaan:
                    expected = chr(ord(target_letter) - 1)
                
                if expected and len(answer_text) == 1:
                    if answer_text != expected:
                        problematic.append({
                            'id': id_soal,
                            'pertanyaan': pertanyaan,
                            'target': target_letter,
                            'expected': expected,
                            'actual': answer_text,
                            'options': f"A={opt_a}, B={opt_b}, C={opt_c}, D={opt_d}"
                        })
                        print(f"\n[MASALAH] DITEMUKAN!")
                        print(f"   ID: {id_soal}")
                        print(f"   Pertanyaan: {pertanyaan}")
                        print(f"   Target: {target_letter}")
                        print(f"   Seharusnya: {expected}")
                        print(f"   Jawaban Sebenarnya: {answer_text}")
                        print(f"   Opsi: {opt_a}, {opt_b}, {opt_c}, {opt_d}")

print("\n" + "="*120)
print(f"Total soal dengan huruf target: {len([r for r in rows for h in target_huruf if h.lower() in r[1].lower()])}")
print(f"Soal bermasalah ditemukan: {len(problematic)}")

if problematic:
    print("\n\nDaftar ID soal untuk dihapus:")
    ids_str = ", ".join(str(p['id']) for p in problematic)
    print(ids_str)

conn.close()
