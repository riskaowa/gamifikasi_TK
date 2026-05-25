#!/usr/bin/env python3
"""
Script untuk menghapus soal huruf B dan Z yang bermasalah.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def delete_problematic_questions():
    """Hapus soal-soal B dan Z yang bermasalah."""
    
    app = create_app()
    
    with app.app_context():
        # ID-ID soal yang perlu dihapus
        problem_ids = [142, 149, 268]
        
        print(f"\n{'='*80}")
        print(f"MENGHAPUS SOAL HURUF B DAN Z YANG BERMASALAH")
        print(f"{'='*80}\n")
        
        deleted_count = 0
        
        for problem_id in problem_ids:
            soal = Soal.query.get(problem_id)
            
            if soal:
                print(f"Menghapus ID {soal.id}: {soal.pertanyaan[:50]}...")
                print(f"  Jawaban DB: {soal.jawaban_benar}")
                print(f"  A: {soal.pilihan_a}, B: {soal.pilihan_b}, C: {soal.pilihan_c}, D: {soal.pilihan_d}")
                
                db.session.delete(soal)
                deleted_count += 1
                print(f"  ✓ Dihapus dari database\n")
            else:
                print(f"⚠ ID {problem_id} tidak ditemukan di database\n")
        
        # Commit perubahan
        try:
            db.session.commit()
            print(f"{'='*80}")
            print(f"BERHASIL MENGHAPUS {deleted_count} SOAL")
            print(f"{'='*80}\n")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ GAGAL: {str(e)}\n")
            return False

if __name__ == '__main__':
    success = delete_problematic_questions()
    sys.exit(0 if success else 1)
