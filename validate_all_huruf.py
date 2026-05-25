"""
Script untuk validasi SEMUA soal huruf dengan detail
Cari soal di mana jawaban tidak sesuai dengan yang diharapkan
"""

import sqlite3
import sys
import os
import re

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

all_rows = cursor.fetchall()

print("VALIDASI LENGKAP SOAL HURUF")
print("="*120)

problematic_full = []
counter = 0

for row in all_rows:
    counter += 1
    id_soal = row[0]
    pertanyaan = row[1] or ""
    opt_a = row[2] or ""
    opt_b = row[3] or ""
    opt_c = row[4] or ""
    opt_d = row[5] or ""
    jawaban_benar = row[6] or ""
    
    # Map jawaban ke opsi
    letter = jawaban_benar.upper() if not jawaban_benar.startswith('option_') else jawaban_benar.replace('option_', '').upper()
    jawaban_map = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
    answer_text = jawaban_map.get(letter if letter in jawaban_map else 'A', "")
    
    # VALIDASI 1: Soal "Huruf apa ini?" atau "Pasangan huruf besar"
    # Jawaban harus berupa SINGLE HURUF KAPITAL
    if "Huruf apa ini" in pertanyaan:
        if not (len(answer_text) == 1 and answer_text.isalpha() and answer_text.isupper()):
            problematic_full.append({
                'id': id_soal,
                'type': 'HURUF_APA_INI_INVALID',
                'pertanyaan': pertanyaan,
                'answer': answer_text,
                'note': f'Jawaban harus single UPPERCASE huruf, ditemukan: {answer_text}'
            })
    
    # VALIDASI 2: Soal "Pasangan huruf besar dari X"
    # Jawaban harus UPPERCASE huruf
    if "Pasangan huruf besar" in pertanyaan:
        if not (len(answer_text) == 1 and answer_text.isalpha() and answer_text.isupper()):
            problematic_full.append({
                'id': id_soal,
                'type': 'PASANGAN_INVALID',
                'pertanyaan': pertanyaan,
                'answer': answer_text,
                'note': f'Jawaban harus UPPERCASE single huruf, ditemukan: {answer_text}'
            })
        # Ekstrak huruf yang ditanyakan
        match_small = re.search(r'dari\s+([a-z])', pertanyaan)
        if match_small:
            expected_upper = match_small.group(1).upper()
            if answer_text != expected_upper:
                problematic_full.append({
                    'id': id_soal,
                    'type': 'PASANGAN_TIDAK_MATCH',
                    'pertanyaan': pertanyaan,
                    'expected': expected_upper,
                    'actual': answer_text,
                    'note': f'Pasangan dari {match_small.group(1)} seharusnya {expected_upper}, tapi {answer_text}'
                })
    
    # VALIDASI 3: Soal "Setelah/Sebelum huruf"
    # Jawaban harus correct next/previous huruf
    if "Setelah huruf" in pertanyaan or "Sebelum huruf" in pertanyaan:
        match_target = re.search(r'huruf\s+([A-Za-z])', pertanyaan)
        if match_target:
            target = match_target.group(1).upper()
            expected = None
            
            if "Setelah" in pertanyaan:
                # Z setelah: wrap to A OR skip entirely
                if target == 'Z':
                    expected = 'A'  # or could be considered an error
                else:
                    expected = chr(ord(target) + 1)
            elif "Sebelum" in pertanyaan:
                # A sebelum: wrap to Z OR skip entirely
                if target == 'A':
                    expected = 'Z'  # or could be considered an error
                else:
                    expected = chr(ord(target) - 1)
            
            if expected and answer_text != expected:
                problematic_full.append({
                    'id': id_soal,
                    'type': 'URUTAN_SALAH',
                    'pertanyaan': pertanyaan,
                    'target': target,
                    'expected': expected,
                    'actual': answer_text,
                    'note': f'Untuk huruf {target}, expected {expected} tapi {answer_text}'
                })
    
    # VALIDASI 4: Soal "Pilih gambar"
    # Jawaban harus berupa KATA, bukan single huruf
    if "Pilih gambar" in pertanyaan:
        if len(answer_text) == 1 and answer_text.isalpha():
            problematic_full.append({
                'id': id_soal,
                'type': 'GAMBAR_INVALID',
                'pertanyaan': pertanyaan,
                'answer': answer_text,
                'note': f'Jawaban gambar harus kata, bukan single huruf: {answer_text}'
            })

print(f"Total soal huruf dianalisis: {counter}")
print(f"Soal bermasalah ditemukan: {len(problematic_full)}\n")

if problematic_full:
    print("DETAIL MASALAH:")
    print("-" * 120)
    for prob in problematic_full:
        print(f"\nID: {prob['id']} - TYPE: {prob['type']}")
        print(f"  Pertanyaan: {prob['pertanyaan']}")
        print(f"  Note: {prob.get('note', '')}")
        if 'expected' in prob:
            print(f"  Expected: {prob['expected']}, Actual: {prob['actual']}")
        else:
            print(f"  Actual Answer: {prob.get('answer', 'N/A')}")
    
    # Generate list of IDs to delete
    ids_to_delete = list(set([p['id'] for p in problematic_full]))
    print(f"\n\nID untuk dihapus ({len(ids_to_delete)}):")
    print(",".join(str(id) for id in sorted(ids_to_delete)))

conn.close()
