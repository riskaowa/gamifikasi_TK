#!/usr/bin/env python3
"""
Script untuk menghapus soal huruf yang sudah korup dan membuat ulang
dengan distribusi jawaban yang lebih seimbang.
"""

import sys
import os
import random
from urllib.parse import quote
from collections import defaultdict

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.question import Soal

app = create_app()

def _svg_data_uri(svg_markup):
    return 'data:image/svg+xml;utf8,' + quote(svg_markup)

def _card_svg(text, fill='#eef7ff', stroke='#8cb6d9', size=64):
    safe = (text or '?')[:14]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
        "<rect x='10' y='10' width='220' height='150' rx='22' fill='" + fill + "' stroke='" + stroke + "' stroke-width='6'/>"
        "<text x='120' y='103' text-anchor='middle' font-family='Arial' font-size='" + str(size) + "' font-weight='700' fill='#103b68'>" + safe + "</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)

LETTER_OBJECTS = {
    'A': ['apel', 'ayam', 'angkot'],
    'B': ['bola', 'buku', 'bebek'],
    'C': ['cacing', 'celana', 'ceri'],
    'D': ['dadu', 'drum', 'dompet'],
    'E': ['es', 'elang', 'ember'],
    'F': ['foto', 'film', 'fanta'],
    'G': ['gajah', 'gelas', 'garpu'],
    'H': ['hujan', 'harimau', 'helm'],
    'I': ['ikan', 'ibu', 'istana'],
    'J': ['jeruk', 'jam', 'jari'],
    'K': ['kucing', 'kursi', 'kado'],
    'L': ['lampu', 'lemari', 'lilin'],
    'M': ['mobil', 'meja', 'mangga'],
    'N': ['nanas', 'naga', 'nenek'],
    'O': ['obor', 'onta', 'obat'],
    'P': ['pisang', 'panda', 'pintu'],
    'Q': ['qori', 'qurban', 'qatar'],
    'R': ['roti', 'rumah', 'radio'],
    'S': ['sapi', 'sepeda', 'susu'],
    'T': ['tas', 'topi', 'tikus'],
    'U': ['ular', 'uban', 'ubi'],
    'V': ['vas', 'vitamin', 'video'],
    'W': ['wortel', 'wajan', 'wayang'],
    'X': ['xilofon', 'xray', 'xenia'],
    'Y': ['yoyo', 'yogurt', 'yak'],
    'Z': ['zebra', 'zip', 'zaitun'],
}

def _mcq_record(
    kategori,
    question_type,
    pertanyaan,
    options,
    answer_index,
    image_question,
    difficulty='mudah',
    option_images=None,
):
    option_images = option_images or [None, None, None, None]
    full_options = list(options[:4])
    while len(full_options) < 4:
        full_options.append(full_options[-1] if full_options else '-')

    letters = ['A', 'B', 'C', 'D']
    return {
        'kategori': kategori,
        'difficulty': difficulty,
        'question_type': question_type,
        'pertanyaan': pertanyaan,
        'pilihan_a': str(full_options[0]),
        'pilihan_b': str(full_options[1]),
        'pilihan_c': str(full_options[2]),
        'pilihan_d': str(full_options[3]),
        'jawaban_benar': letters[max(0, min(3, int(answer_index)))],
        'image_question': image_question,
        'image_option_a': option_images[0],
        'image_option_b': option_images[1],
        'image_option_c': option_images[2],
        'image_option_d': option_images[3],
    }

def generate_huruf_questions_balanced():
    """
    Generate soal huruf dengan distribusi jawaban yang lebih seimbang.
    """
    records = []
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    # Buat tracking untuk distribusi jawaban
    answer_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    
    for idx, letter in enumerate(letters):
        prev_letter = letters[(idx - 1) % len(letters)]
        next_letter = letters[(idx + 1) % len(letters)]
        jump_letter = letters[(idx + 5) % len(letters)]

        # Soal 1: recognize_letter
        # Acak jawaban untuk ini
        answer_pos = idx % 4
        options_shuffled = [letter, prev_letter, next_letter, jump_letter]
        while len(options_shuffled) < 4:
            options_shuffled.append(letter)
        random.Random(f"recognize-{letter}").shuffle(options_shuffled)
        answer_pos = options_shuffled.index(letter)
        
        records.append(_mcq_record(
            kategori='huruf',
            question_type='recognize_letter',
            pertanyaan='Huruf apa ini?',
            options=options_shuffled,
            answer_index=answer_pos,
            image_question=_card_svg(letter, fill='#e3f2fd', stroke='#64b5f6', size=92),
            difficulty='mudah'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1

        # Soal 2: match_letter (case matching)
        lower = letter.lower()
        options = [letter, prev_letter, next_letter, jump_letter]
        random.Random(f"match-{letter}").shuffle(options)
        answer_pos = options.index(letter)
        
        records.append(_mcq_record(
            kategori='huruf',
            question_type='match_letter',
            pertanyaan=f'Pasangan huruf besar dari {lower} adalah ...',
            options=options,
            answer_index=answer_pos,
            image_question=_card_svg(lower, fill='#f1f8e9', stroke='#aed581', size=88),
            difficulty='mudah'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1

        # Soal 3: letter_sequence
        options = [next_letter, prev_letter, letter, jump_letter]
        random.Random(f"sequence-{letter}").shuffle(options)
        answer_pos = options.index(next_letter)
        
        records.append(_mcq_record(
            kategori='huruf',
            question_type='letter_sequence',
            pertanyaan=f'Setelah huruf {letter} adalah ...',
            options=options,
            answer_index=answer_pos,
            image_question=_card_svg(letter, fill='#fff8e1', stroke='#ffd54f', size=88),
            difficulty='mudah' if idx < 20 else 'sedang'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1

        # Soal 4: before_letter
        options = [prev_letter, next_letter, jump_letter, letter]
        random.Random(f"before-{letter}").shuffle(options)
        answer_pos = options.index(prev_letter)
        
        records.append(_mcq_record(
            kategori='huruf',
            question_type='before_letter',
            pertanyaan=f'Sebelum huruf {letter} adalah ...',
            options=options,
            answer_index=answer_pos,
            image_question=_card_svg(letter, fill='#fce4ec', stroke='#f48fb1', size=88),
            difficulty='mudah' if idx < 20 else 'sedang'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1

        # Soal 5: initial_letter (PENTING - jawaban harus dimulai dengan huruf yang benar)
        object_words = LETTER_OBJECTS.get(letter, ['apel', 'bola', 'kucing'])
        correct_word = object_words[0]
        wrong1 = LETTER_OBJECTS.get(next_letter, ['mobil'])[0]
        wrong2 = LETTER_OBJECTS.get(prev_letter, ['tas'])[0]
        wrong3 = LETTER_OBJECTS.get(jump_letter, ['buku'])[0]

        option_words = [correct_word, wrong1, wrong2, wrong3]
        random.Random(f"initial-{letter}").shuffle(option_words)
        answer_pos = option_words.index(correct_word)
        
        option_images = [
            _card_svg(correct_word, fill='#fffde7', stroke='#fff176', size=36),
            _card_svg(wrong1, fill='#fffde7', stroke='#fff176', size=36),
            _card_svg(wrong2, fill='#fffde7', stroke='#fff176', size=36),
            _card_svg(wrong3, fill='#fffde7', stroke='#fff176', size=36),
        ]

        records.append(_mcq_record(
            kategori='huruf',
            question_type='initial_letter',
            pertanyaan=f'Pilih gambar yang diawali huruf {letter}.',
            options=option_words,
            answer_index=answer_pos,
            image_question=_card_svg(letter, fill='#ede7f6', stroke='#9575cd', size=96),
            option_images=option_images,
            difficulty='sedang'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1
    
    # Pola isian alfabet sederhana
    for idx in range(0, len(letters) - 3):
        a = letters[idx]
        b = letters[idx + 1]
        missing = letters[idx + 2]
        d = letters[idx + 3]
        wrong = letters[(idx + 6) % len(letters)]
        
        options = [missing, b, wrong, a]
        random.Random(f"fill-{idx}").shuffle(options)
        answer_pos = options.index(missing)
        
        records.append(_mcq_record(
            kategori='huruf',
            question_type='fill_blank_letter',
            pertanyaan='Isi huruf yang kosong.',
            options=options,
            answer_index=answer_pos,
            image_question=_card_svg(f'{a} {b} _ {d}', fill='#e8eaf6', stroke='#9fa8da', size=44),
            difficulty='sedang'
        ))
        answer_distribution[['A', 'B', 'C', 'D'][answer_pos]] += 1
    
    print("Distribusi jawaban yang dibuat:")
    total = len(records)
    for answer in ['A', 'B', 'C', 'D']:
        count = answer_distribution[answer]
        pct = (count / total) * 100 if total > 0 else 0
        print(f"  {answer}: {count:3d}/{total} ({pct:5.1f}%)")
    
    return records

def replace_huruf_questions():
    """
    Menghapus semua soal huruf lama dan membuat yang baru.
    """
    with app.app_context():
        print("MENGGANTI SOAL HURUF")
        print("="*80)
        
        # Hapus soal huruf lama
        old_count = Soal.query.filter_by(kategori='huruf').count()
        Soal.query.filter_by(kategori='huruf').delete()
        db.session.commit()
        print(f"\n✓ {old_count} soal huruf lama dihapus")
        
        # Generate soal baru
        print(f"\nMembuat soal huruf baru...")
        new_records = generate_huruf_questions_balanced()
        
        # Insert ke database
        for record in new_records:
            soal = Soal(
                kategori=record['kategori'],
                difficulty=record['difficulty'],
                question_type=record['question_type'],
                pertanyaan=record['pertanyaan'],
                pilihan_a=record['pilihan_a'],
                pilihan_b=record['pilihan_b'],
                pilihan_c=record['pilihan_c'],
                pilihan_d=record['pilihan_d'],
                jawaban_benar=record['jawaban_benar'],
                image_question=record['image_question'],
                image_option_a=record['image_option_a'],
                image_option_b=record['image_option_b'],
                image_option_c=record['image_option_c'],
                image_option_d=record['image_option_d'],
                use_in_daily_mission=True,
                use_in_adventure_map=True,
            )
            db.session.add(soal)
        
        db.session.commit()
        print(f"✓ {len(new_records)} soal huruf baru dibuat dan tersimpan")
        
        # Verifikasi
        new_count = Soal.query.filter_by(kategori='huruf').count()
        print(f"\nVerifikasi:")
        print(f"  Total soal huruf: {new_count}")
        
        # Cek distribusi
        answer_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for soal in Soal.query.filter_by(kategori='huruf').all():
            answer_counts[soal.jawaban_benar] += 1
        
        print(f"\nDistribusi jawaban:")
        for answer in ['A', 'B', 'C', 'D']:
            count = answer_counts[answer]
            pct = (count / new_count) * 100
            print(f"  {answer}: {count:3d}/{new_count} ({pct:5.1f}%)")

if __name__ == '__main__':
    replace_huruf_questions()
    print("\n" + "="*80)
    print("Penggantian soal selesai")
