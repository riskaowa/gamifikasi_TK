from urllib.parse import quote


OBJECTS = [
    'apel',
    'bola',
    'buku',
    'ikan',
    'kucing',
    'mobil',
    'pisang',
    'tas',
]

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


def _count_svg(count, label):
    count = max(1, min(30, int(count)))
    columns = 5
    rows = max(1, (count + columns - 1) // columns)
    radius = 10 if count > 20 else 11 if count > 15 else 12
    gap_x = 36
    gap_y = 28 if rows >= 5 else 32
    dots = []
    for idx in range(count):
        col = idx % columns
        row = idx // columns
        cx = 48 + (col * gap_x)
        cy = 42 + (row * gap_y)
        dots.append("<circle cx='" + str(cx) + "' cy='" + str(cy) + "' r='" + str(radius) + "' fill='#ffb74d' stroke='#ef6c00' stroke-width='3'/>")

    safe_label = (label or 'benda')[:12]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
        "<rect x='10' y='10' width='220' height='150' rx='20' fill='#fff7ec' stroke='#ffd59a' stroke-width='6'/>"
        + ''.join(dots) +
        "<text x='120' y='154' text-anchor='middle' font-family='Arial' font-size='20' fill='#8a4f08'>" + safe_label + "</text>"
        "<text x='205' y='32' text-anchor='middle' font-family='Arial' font-size='18' font-weight='700' fill='#b85c38'>" + str(count) + "</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


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


def _generate_angka_questions(target_count):
    records = []

    for number in range(1, 31):
        prev_num = 30 if number == 1 else number - 1
        next_num = 1 if number == 30 else number + 1
        jump_num = ((number + 7 - 1) % 30) + 1

        records.append(_mcq_record(
            kategori='angka',
            question_type='count_objects',
            pertanyaan='Hitung gambarnya. Pilih angka yang benar.',
            options=[str(number), str(prev_num), str(next_num), str(jump_num)],
            answer_index=0,
            image_question=_count_svg(number, OBJECTS[number % len(OBJECTS)]),
            difficulty='mudah'
        ))

        records.append(_mcq_record(
            kategori='angka',
            question_type='recognize_number',
            pertanyaan='Ini angka berapa?',
            options=[str(number), str(next_num), str(prev_num), str(jump_num)],
            answer_index=0,
            image_question=_card_svg(str(number), fill='#e8f5e9', stroke='#81c784', size=86),
            difficulty='mudah'
        ))

    # Isian pola sederhana (tetap MCQ)
    for base in range(1, 26):
        missing = base + 2
        sequence = f'{base}, {base + 1}, _, {base + 3}'
        options = [str(missing), str(base), str(base + 4), str(base + 1)]
        records.append(_mcq_record(
            kategori='angka',
            question_type='fill_blank_number',
            pertanyaan='Isi angka yang kosong.',
            options=options,
            answer_index=0,
            image_question=_card_svg(sequence, fill='#f3e5f5', stroke='#ce93d8', size=32),
            difficulty='sedang'
        ))

    return records[:target_count]


def _generate_huruf_questions(target_count):
    records = []
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    for idx, letter in enumerate(letters):
        prev_letter = letters[(idx - 1) % len(letters)]
        next_letter = letters[(idx + 1) % len(letters)]
        jump_letter = letters[(idx + 5) % len(letters)]

        records.append(_mcq_record(
            kategori='huruf',
            question_type='recognize_letter',
            pertanyaan='Huruf apa ini?',
            options=[letter, prev_letter, next_letter, jump_letter],
            answer_index=0,
            image_question=_card_svg(letter, fill='#e3f2fd', stroke='#64b5f6', size=92),
            difficulty='mudah'
        ))

        lower = letter.lower()
        records.append(_mcq_record(
            kategori='huruf',
            question_type='match_upper_lower',
            pertanyaan=f'Pasangan huruf besar dari {lower} adalah ...',
            options=[letter, prev_letter, next_letter, jump_letter],
            answer_index=0,
            image_question=_card_svg(lower, fill='#f1f8e9', stroke='#aed581', size=88),
            difficulty='mudah'
        ))

        records.append(_mcq_record(
            kategori='huruf',
            question_type='letter_sequence',
            pertanyaan=f'Setelah huruf {letter} adalah ...',
            options=[next_letter, prev_letter, letter, jump_letter],
            answer_index=0,
            image_question=_card_svg(letter, fill='#fff8e1', stroke='#ffd54f', size=88),
            difficulty='mudah' if idx < 20 else 'sedang'
        ))

        records.append(_mcq_record(
            kategori='huruf',
            question_type='before_letter',
            pertanyaan=f'Sebelum huruf {letter} adalah ...',
            options=[prev_letter, next_letter, jump_letter, letter],
            answer_index=0,
            image_question=_card_svg(letter, fill='#fce4ec', stroke='#f48fb1', size=88),
            difficulty='mudah' if idx < 20 else 'sedang'
        ))

        object_words = LETTER_OBJECTS.get(letter, ['apel', 'bola', 'kucing'])
        correct_word = object_words[0]
        wrong1 = LETTER_OBJECTS.get(next_letter, ['mobil'])[0]
        wrong2 = LETTER_OBJECTS.get(prev_letter, ['tas'])[0]
        wrong3 = LETTER_OBJECTS.get(jump_letter, ['buku'])[0]

        option_words = [correct_word, wrong1, wrong2, wrong3]
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
            answer_index=0,
            image_question=_card_svg(letter, fill='#ede7f6', stroke='#9575cd', size=96),
            option_images=option_images,
            difficulty='sedang'
        ))

    # Pola isian alfabet sederhana
    for idx in range(0, len(letters) - 3):
        a = letters[idx]
        b = letters[idx + 1]
        missing = letters[idx + 2]
        d = letters[idx + 3]
        wrong = letters[(idx + 6) % len(letters)]
        records.append(_mcq_record(
            kategori='huruf',
            question_type='fill_blank_letter',
            pertanyaan='Isi huruf yang kosong.',
            options=[missing, b, wrong, a],
            answer_index=0,
            image_question=_card_svg(f'{a} {b} _ {d}', fill='#e8eaf6', stroke='#9fa8da', size=44),
            difficulty='sedang'
        ))

    return records[:target_count]


def _generate_campuran_questions(target_count):
    records = []
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    for number in range(1, 31):
        letter = letters[(number - 1) % len(letters)]
        wrong_letter_1 = letters[number % len(letters)]
        wrong_letter_2 = letters[(number + 4) % len(letters)]
        wrong_number = 1 if number == 30 else number + 1

        prompt = f'Ada {number if number <= 10 else (number % 10) + 1} benda dan huruf {letter}. Pasangan yang benar mana?'

        pair_ok = f'{number}-{letter}'
        pair_wrong_1 = f'{wrong_number}-{letter}'
        pair_wrong_2 = f'{number}-{wrong_letter_1}'
        pair_wrong_3 = f'{wrong_number}-{wrong_letter_2}'

        records.append(_mcq_record(
            kategori='campuran',
            question_type='mixed_pair_match',
            pertanyaan=prompt,
            options=[pair_ok, pair_wrong_1, pair_wrong_2, pair_wrong_3],
            answer_index=0,
            image_question=_count_svg(number if number <= 10 else (number % 10) + 1, letter),
            difficulty='mudah' if number <= 15 else 'sedang'
        ))

        obj = OBJECTS[number % len(OBJECTS)]
        first = obj[0].upper()
        wrong_a = letters[(letters.index(first) + 1) % len(letters)]
        wrong_b = letters[(letters.index(first) + 3) % len(letters)]
        wrong_c = letters[(letters.index(first) + 7) % len(letters)]

        option_images = [
            _card_svg(first, fill='#e0f2f1', stroke='#80cbc4', size=86),
            _card_svg(wrong_a, fill='#e0f2f1', stroke='#80cbc4', size=86),
            _card_svg(wrong_b, fill='#e0f2f1', stroke='#80cbc4', size=86),
            _card_svg(wrong_c, fill='#e0f2f1', stroke='#80cbc4', size=86),
        ]

        records.append(_mcq_record(
            kategori='campuran',
            question_type='object_initial_and_count',
            pertanyaan=f'Gambar menunjukkan {number if number <= 10 else (number % 10) + 1} {obj}. Pilih huruf awal yang benar.',
            options=[first, wrong_a, wrong_b, wrong_c],
            answer_index=0,
            image_question=_count_svg(number if number <= 10 else (number % 10) + 1, obj),
            option_images=option_images,
            difficulty='sedang'
        ))

    # Tambah pola campuran angka + huruf
    for idx in range(1, max(41, target_count + 1)):
        number = (idx % 20) + 1
        letter = letters[(idx + 2) % len(letters)]
        wrong_number = number + 2 if number <= 18 else number - 2
        wrong_letter = letters[(letters.index(letter) + 2) % len(letters)]

        records.append(_mcq_record(
            kategori='campuran',
            question_type='mixed_fill_blank',
            pertanyaan='Isi pasangan yang benar.',
            options=[f'{number}-{letter}', f'{wrong_number}-{letter}', f'{number}-{wrong_letter}', f'{wrong_number}-{wrong_letter}'],
            answer_index=0,
            image_question=_card_svg(f'{number} _', fill='#fbe9e7', stroke='#ffab91', size=54),
            difficulty='sedang'
        ))

    return records[:target_count]


def build_question_bank(total_angka=120, total_huruf=120, total_campuran=120):
    angka = _generate_angka_questions(max(0, int(total_angka)))
    huruf = _generate_huruf_questions(max(0, int(total_huruf)))
    campuran = _generate_campuran_questions(max(0, int(total_campuran)))
    return angka + huruf + campuran


def seed_question_bank(session, SoalModel, targets=None):
    targets = targets or {
        'angka': 120,
        'huruf': 120,
        'campuran': 120,
    }

    need_angka = max(0, int(targets.get('angka', 0)))
    need_huruf = max(0, int(targets.get('huruf', 0)))
    need_campuran = max(0, int(targets.get('campuran', 0)))

    existing_angka = SoalModel.query.filter_by(kategori='angka').count()
    existing_huruf = SoalModel.query.filter_by(kategori='huruf').count()
    existing_campuran = SoalModel.query.filter_by(kategori='campuran').count()

    add_angka = max(0, need_angka - existing_angka)
    add_huruf = max(0, need_huruf - existing_huruf)
    add_campuran = max(0, need_campuran - existing_campuran)

    if add_angka == 0 and add_huruf == 0 and add_campuran == 0:
        return 0

    generated = build_question_bank(
        total_angka=max(need_angka, add_angka),
        total_huruf=max(need_huruf, add_huruf),
        total_campuran=max(need_campuran, add_campuran),
    )

    inserted = []
    counters = {
        'angka': 0,
        'huruf': 0,
        'campuran': 0,
    }
    limits = {
        'angka': add_angka,
        'huruf': add_huruf,
        'campuran': add_campuran,
    }

    for row in generated:
        kategori = row.get('kategori')
        if kategori not in counters:
            continue
        if counters[kategori] >= limits[kategori]:
            continue

        inserted.append(SoalModel(**row))
        counters[kategori] += 1

    if inserted:
        session.bulk_save_objects(inserted)
        session.commit()

    return len(inserted)
