from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, session, jsonify, Response, current_app, abort, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import db, socketio
from app.models.user import User
from app.models.audio_file import AudioFile
from app.models.question import Soal
from app.models.skor import Skor
from app.models.progres_harian import ProgresHarian
from app.models.badge import Badge
from app.models.user_badge import UserBadge
from app.models.game_play import GamePlay
from app.models.game_session import GameSession
from app.models.user_progress import UserProgress
from app.models.user_daily_login import UserDailyLogin
from app.models.user_daily_status import UserDailyStatus
from app.models.user_game_history import UserGameHistory
from app.models.password_reset_log import PasswordResetLog
from app.models.user_history import UserHistory
from app.models.user_scores import UserScore
from app.models.user_certificate import UserCertificate
from app.models.access_time import AccessTime
from app.models.parent_student import ParentStudent
from app.models.teacher_note import TeacherNote
from app.models.daily_mission import DailyMissionRun
from app.models.daily_mission_access_time import DailyMissionAccessTime
from app.models.student_menu_access_time import StudentMenuAccessTime
from app.models.materi import Materi
from app.models.question_usage import QuestionUsage
from app.models.adventure_question_map import AdventureQuestionMap
from app.models.daily_mission_question import DailyMissionQuestion
from flask_socketio import join_room, leave_room
from werkzeug.utils import secure_filename
import random
import io
import mimetypes
import os
import secrets
import string
import html
from urllib.parse import quote
from datetime import date, datetime, timedelta, time
from sqlalchemy import case, func

main = Blueprint('main', __name__)

# Tambahkan route edit/hapus guru di sini
@main.route('/guru-dashboard/edit-guru/<int:user_id>', methods=['POST'])
@login_required
def guru_edit_guru(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    guru = User.query.get_or_404(user_id)
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    role = request.form.get('role', '').strip().lower()
    if not name or not username or not role:
        flash('Nama, username, dan role wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-guru')
    if User.query.filter(User.username == username, User.id != user_id).first():
        flash(f'Username "{username}" sudah digunakan.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-guru')
    guru.name = name
    guru.username = username
    guru.role = role
    db.session.commit()
    flash('Data guru berhasil diperbarui.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-guru')

@main.route('/guru-dashboard/hapus-guru/<int:user_id>', methods=['POST'])
@login_required
def guru_hapus_guru(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403
    guru = User.query.get_or_404(user_id)
    if guru.role not in ['guru', 'admin']:
        flash('Akun yang dipilih bukan guru/admin.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-guru')
    db.session.delete(guru)
    db.session.commit()
    flash('Akun guru berhasil dihapus.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-guru')

GAME_KEYS = ['huruf', 'angka', 'warna']
STUDENT_ROLES = ('murid', 'user', 'anak')
HURUF_LEVEL_RULES = [
    {'level': 1, 'question_count': 5, 'time_limit': 60, 'weight': 1},
    {'level': 2, 'question_count': 5, 'time_limit': 50, 'weight': 2},
    {'level': 3, 'question_count': 5, 'time_limit': 40, 'weight': 3},
    {'level': 4, 'question_count': 5, 'time_limit': 30, 'weight': 4},
    {'level': 5, 'question_count': 5, 'time_limit': 20, 'weight': 5},
]
ANGKA_LEVEL_RULES = [
    {'level': 1, 'question_count': 5, 'time_limit': 60, 'weight': 1},
    {'level': 2, 'question_count': 5, 'time_limit': 50, 'weight': 2},
    {'level': 3, 'question_count': 5, 'time_limit': 40, 'weight': 3},
    {'level': 4, 'question_count': 5, 'time_limit': 30, 'weight': 4},
    {'level': 5, 'question_count': 5, 'time_limit': 20, 'weight': 5},
]
WARNA_BENTUK_LEVEL_RULES = [
    {'level': 1, 'question_count': 5, 'time_limit': 60, 'weight': 1},
    {'level': 2, 'question_count': 5, 'time_limit': 50, 'weight': 2},
    {'level': 3, 'question_count': 5, 'time_limit': 40, 'weight': 3},
    {'level': 4, 'question_count': 5, 'time_limit': 30, 'weight': 4},
    {'level': 5, 'question_count': 5, 'time_limit': 20, 'weight': 5},
]
ADVENTURE_GAMES = ['huruf', 'angka', 'warna']
DEFAULT_ACCESS_START = time(8, 0)
DEFAULT_ACCESS_END = time(22, 0)
DEFAULT_DAILY_MISSION_ACCESS_START = time(8, 0)
DEFAULT_DAILY_MISSION_ACCESS_END = time(20, 0)
DEFAULT_MENU_ACCESS_START = time(8, 0)
DEFAULT_MENU_ACCESS_END = time(22, 0)
DAILY_MISSION_TIME_LIMIT_SECONDS = 420
DAILY_MISSION_TOTAL_QUESTIONS = 2
MISSION_REPEAT_COOLDOWN_DAYS = 3
MISSION_REQUIRED_CATEGORIES = ['huruf', 'angka', 'warna_bentuk']
MISSION_CATEGORY_ALIASES = {
    'huruf': 'huruf',
    'angka': 'angka',
    'warna': 'warna_bentuk',
    'bentuk_bangun_ruang': 'warna_bentuk',
    'bentuk': 'warna_bentuk',
    'warna-bentuk': 'warna_bentuk',
    'warna_bentuk': 'warna_bentuk'
}
ACCOUNT_MANAGEMENT_ROLES = ('murid', 'orangtua', 'orang_tua')
QUESTION_CATEGORIES = ['huruf', 'angka', 'warna', 'bentuk_bangun_ruang']
QUESTION_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
QUESTION_UPLOAD_SUBDIR = os.path.join('uploads', 'question_bank')

NUMBER_WORDS_ID = {
    0: 'nol',
    1: 'satu',
    2: 'dua',
    3: 'tiga',
    4: 'empat',
    5: 'lima',
    6: 'enam',
    7: 'tujuh',
    8: 'delapan',
    9: 'sembilan',
    10: 'sepuluh',
    11: 'sebelas',
    12: 'dua belas',
    13: 'tiga belas',
    14: 'empat belas',
    15: 'lima belas',
    16: 'enam belas',
    17: 'tujuh belas',
    18: 'delapan belas',
    19: 'sembilan belas',
    20: 'dua puluh',
    21: 'dua puluh satu',
    22: 'dua puluh dua',
    23: 'dua puluh tiga',
    24: 'dua puluh empat',
    25: 'dua puluh lima',
    26: 'dua puluh enam',
    27: 'dua puluh tujuh',
    28: 'dua puluh delapan',
    29: 'dua puluh sembilan',
    30: 'tiga puluh',
}

COLOR_VISUAL_MAP = {
    'merah': '#e53935',
    'biru': '#1e88e5',
    'kuning': '#fdd835',
    'hijau': '#43a047',
    'oranye': '#fb8c00',
    'ungu': '#8e24aa',
    'putih': '#f5f5f5',
    'hitam': '#212121',
    'cokelat': '#8d6e63',
    'abu-abu': '#9e9e9e',
    'abu abu': '#9e9e9e',
}

SHAPE_VISUAL_SET = {'bola', 'kubus', 'balok', 'tabung', 'kerucut', 'limas', 'prisma'}


def format_hhmm(value):
    if not value:
        return '--:--'
    return value.strftime('%H:%M')


def normalize_question_category(raw_category):
    key = (raw_category or '').strip().lower().replace('-', '_').replace(' ', '_')
    if key in ['huruf', 'angka', 'warna', 'bentuk_bangun_ruang']:
        return key
    if key in ['bentuk', 'bangun_ruang', 'bentuk_bangun']:
        return 'bentuk_bangun_ruang'
    if key in ['warna_bentuk', 'warna_dan_bentuk']:
        return 'warna'
    return None


def get_adventure_game_key_for_category(category):
    normalized = normalize_question_category(category)
    if normalized == 'huruf':
        return 'huruf'
    if normalized == 'angka':
        return 'angka'
    if normalized in ['warna', 'bentuk_bangun_ruang']:
        return 'warna'
    return None


def _allowed_question_image(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower().strip()
    return ext in QUESTION_ALLOWED_EXTENSIONS


def _save_question_image(file_storage, image_prefix):
    if not file_storage:
        return None

    original_name = (file_storage.filename or '').strip()
    if not original_name:
        return None

    if not _allowed_question_image(original_name):
        raise ValueError('Format gambar tidak didukung. Gunakan PNG/JPG/JPEG/WEBP/GIF.')

    safe_name = secure_filename(original_name)
    ext = safe_name.rsplit('.', 1)[1].lower()
    random_name = f"{image_prefix}_{secrets.token_hex(8)}.{ext}"

    upload_dir = os.path.join(current_app.static_folder, QUESTION_UPLOAD_SUBDIR)
    os.makedirs(upload_dir, exist_ok=True)

    output_path = os.path.join(upload_dir, random_name)
    file_storage.save(output_path)

    return f"{QUESTION_UPLOAD_SUBDIR.replace('\\', '/')}/{random_name}"


def _delete_question_image(image_path):
    value = (image_path or '').strip().replace('\\', '/')
    if not value:
        return
    if not value.startswith(f"{QUESTION_UPLOAD_SUBDIR.replace('\\', '/')}/"):
        return

    absolute = os.path.abspath(os.path.join(current_app.static_folder, value))
    static_root = os.path.abspath(current_app.static_folder)
    if not absolute.startswith(static_root):
        return
    if os.path.exists(absolute):
        try:
            os.remove(absolute)
        except OSError:
            pass


def _set_question_usages(question_id, include_daily_mission, include_adventure_map, category):
    QuestionUsage.query.filter_by(question_id=question_id).delete()

    if include_daily_mission:
        db.session.add(QuestionUsage(
            question_id=question_id,
            context='daily_mission',
            game_key=None,
            is_active=True,
        ))

    if include_adventure_map:
        game_key = get_adventure_game_key_for_category(category)
        if game_key:
            db.session.add(QuestionUsage(
                question_id=question_id,
                context='adventure_map',
                game_key=game_key,
                is_active=True,
            ))


def _question_is_enabled_for_daily_mission(question_id):
    return db.session.query(QuestionUsage.id).filter_by(
        question_id=question_id,
        context='daily_mission',
        is_active=True,
    ).first() is not None


def _question_is_enabled_for_adventure(question_id, game_key):
    return db.session.query(QuestionUsage.id).filter_by(
        question_id=question_id,
        context='adventure_map',
        game_key=game_key,
        is_active=True,
    ).first() is not None


def _get_soal_by_ids(ids):
    if not ids:
        return {}
    rows = Soal.query.filter(Soal.id.in_(ids)).all()
    return {row.id: row for row in rows}


def _get_adventure_map_candidate_questions():
    """Return semua pertanyaan yang tersedia di Peta Pertualangan."""
    adventure_question_ids = {
        slot.question_id
        for slot in AdventureQuestionMap.query.filter(AdventureQuestionMap.question_id.isnot(None)).all()
        if slot.question_id
    }
    if adventure_question_ids:
        return Soal.query.filter(Soal.id.in_(adventure_question_ids)).all()

    usage_rows = db.session.query(QuestionUsage.question_id).filter(
        QuestionUsage.context == 'adventure_map',
        QuestionUsage.is_active == True
    ).distinct().all()
    question_ids = [row.question_id for row in usage_rows if row.question_id]
    if question_ids:
        return Soal.query.filter(Soal.id.in_(question_ids)).all()

    return []


def _is_valid_adventure_answer_key(value):
    normalized = (value or '').strip().lower()
    return normalized in {'a', 'b', 'c', 'd', 'option_a', 'option_b', 'option_c', 'option_d'}


def _build_question_payload_from_row(row, game_key, level, number_in_level, global_index):
    if not _is_valid_adventure_answer_key(row.jawaban_benar):
        return None

    answer_letter = Soal.answer_key_to_letter(row.jawaban_benar)
    if answer_letter not in {'A', 'B', 'C', 'D'}:
        return None

    option_map = {
        'A': (row.pilihan_a or '').strip(),
        'B': (row.pilihan_b or '').strip(),
        'C': (row.pilihan_c or '').strip(),
        'D': (row.pilihan_d or '').strip(),
    }

    answer_text = option_map.get(answer_letter)
    if not answer_text:
        return None

    options = [value for value in [option_map['A'], option_map['B'], option_map['C'], option_map['D']] if value]
    options = list(dict.fromkeys(options))
    if not options or answer_text not in options:
        return None

    option_rng = random.Random(f"adventure-{game_key}-{row.id}-{date.today().isoformat()}-{global_index}")
    option_rng.shuffle(options)

    if (row.question_type or '').strip().lower() == 'count_objects' and answer_text.isdigit():
        question_image = _count_objects_svg_data(int(answer_text), 'benda')
    else:
        question_image = _build_static_image_url(row.image_question)
        if not question_image:
            question_image = _build_visual_image_data(answer_text, row.kategori)

    option_image_map_raw = {
        option_map['A']: _build_static_image_url(row.image_option_a),
        option_map['B']: _build_static_image_url(row.image_option_b),
        option_map['C']: _build_static_image_url(row.image_option_c),
        option_map['D']: _build_static_image_url(row.image_option_d),
    }
    option_images = {}
    for option_value in options:
        image_value = option_image_map_raw.get(option_value)
        if not image_value:
            image_value = _build_visual_image_data(option_value, row.kategori)
        option_images[option_value] = image_value

    level_rule = next((r for r in HURUF_LEVEL_RULES if r['level'] == level), None)
    if game_key == 'angka':
        level_rule = next((r for r in ANGKA_LEVEL_RULES if r['level'] == level), None)
    elif game_key == 'warna':
        level_rule = next((r for r in WARNA_BENTUK_LEVEL_RULES if r['level'] == level), None)

    level_rule = level_rule or {'time_limit': 60, 'weight': 1}

    return {
        'question_id': f"db-{row.id}-{global_index}",
        'display': answer_text,
        'display_value': answer_text,
        'prompt': _prompt_for_game(game_key),
        'options': options,
        'option_images': option_images,
        'question_image': question_image,
        'answer': answer_text,
        'level': level,
        'number_in_level': number_in_level,
        'time_limit': level_rule['time_limit'],
        'weight': level_rule['weight']
    }


def ensure_adventure_question_map(game_key, level_rules):
    available_rows = _rows_for_adventure_game(game_key)
    if not available_rows:
        return []

    slot_defs = []
    for rule in level_rules:
        for order in range(1, rule['question_count'] + 1):
            slot_defs.append((rule['level'], order))

    existing = AdventureQuestionMap.query.filter_by(game_key=game_key).all()
    slot_map = {(row.level, row.question_order): row for row in existing}

    changed = False
    pool = list(available_rows)
    random.Random(f"adventure-map-seed-{game_key}").shuffle(pool)

    cursor = 0
    for level, order in slot_defs:
        slot = slot_map.get((level, order))
        if not slot:
            slot = AdventureQuestionMap(game_key=game_key, level=level, question_order=order, question_id=None)
            db.session.add(slot)
            slot_map[(level, order)] = slot
            changed = True

        if slot.question_id:
            continue

        row = pool[cursor % len(pool)]
        cursor += 1
        slot.question_id = row.id
        changed = True

    if changed:
        db.session.commit()

    return list(slot_map.values())


def get_fixed_adventure_questions(game_key, level_rules):
    slots = ensure_adventure_question_map(game_key, level_rules)
    if not slots:
        return []

    ids = [slot.question_id for slot in slots if slot.question_id]
    question_map = _get_soal_by_ids(ids)
    fallback_pool = _rows_for_adventure_game(game_key)
    fallback_cursor = 0
    changed = False

    sorted_slots = sorted(slots, key=lambda s: (s.level, s.question_order))
    result = []
    for idx, slot in enumerate(sorted_slots):
        row = question_map.get(slot.question_id)
        if not row and fallback_pool:
            row = fallback_pool[fallback_cursor % len(fallback_pool)]
            fallback_cursor += 1
            slot.question_id = row.id
            changed = True

        if not row:
            continue

        payload = _build_question_payload_from_row(
            row=row,
            game_key=game_key,
            level=slot.level,
            number_in_level=slot.question_order,
            global_index=idx,
        )
        if payload:
            result.append(payload)

    if changed:
        db.session.commit()

    return result


def get_or_generate_daily_mission_rows(today):
    """
    Mengambil atau menghasilkan soal misi harian untuk tanggal tertentu.
    
    Ketentuan:
    - Semua murid mendapatkan soal yang sama setiap hari
    - Soal disimpan ke database agar tidak berubah saat refresh
    - Hanya menggunakan soal aktif (ada gambar)
    - Tidak ada duplikasi soal dalam sehari
    - Fallback jika database kosong
    """
    # Import model soal di dalam fungsi untuk memastikan ketersediaan
    from app.models.question import Soal as _SoalModel
    # 1. Cek apakah sudah ada soal untuk hari ini
    rows = DailyMissionQuestion.query.filter_by(tanggal=today).order_by(DailyMissionQuestion.question_order.asc()).all()
    if len(rows) >= DAILY_MISSION_TOTAL_QUESTIONS:
        return rows

    # 2. Ambil kandidat soal dari tabel soal (Soal Aktif)
    #    Hanya soal yang memiliki gambar dan kategori valid untuk misi harian
    all_questions = _SoalModel.query.all()
    candidates = []
    for question in all_questions:
        # Cek apakah soal memiliki gambar (indikator soal aktif)
        has_image = bool(question.image_question)
        # Cek kategori valid untuk misi harian
        valid_category = normalize_mission_category(question.kategori)
        if has_image and valid_category:
            candidates.append(question)

    # 3. Fallback: jika tidak ada soal dengan gambar, gunakan semua soal yang valid kategori
    if not candidates:
        for question in all_questions:
            if normalize_mission_category(question.kategori):
                candidates.append(question)

    # 4. Fallback terakhir: jika tetap tidak ada, coba semua soal
    if not candidates:
        candidates = list(all_questions)

    if not candidates:
        return rows

    # 5. Ambil kandidat pertama dari Peta Pertualangan
    existing_question_ids = {row.question_id for row in rows if row.question_id}
    selected_questions = []
    adventure_candidates = _get_adventure_map_candidate_questions()
    if adventure_candidates:
        rng = random.Random(f"daily-mission-{today.isoformat()}")
        rng.shuffle(adventure_candidates)
        for question in adventure_candidates:
            if len(rows) + len(selected_questions) >= DAILY_MISSION_TOTAL_QUESTIONS:
                break
            if question.id not in existing_question_ids and question.id not in {q.id for q in selected_questions}:
                selected_questions.append(question)

    # 6. Jika Peta Pertualangan belum cukup, isi dengan kandidat misi harian biasa
    if len(rows) + len(selected_questions) < DAILY_MISSION_TOTAL_QUESTIONS:
        rng = random.Random(f"daily-mission-{today.isoformat()}")
        rng.shuffle(candidates)
        for question in candidates:
            if len(rows) + len(selected_questions) >= DAILY_MISSION_TOTAL_QUESTIONS:
                break
            if question.id not in existing_question_ids and question.id not in {q.id for q in selected_questions}:
                selected_questions.append(question)

    # 7. Simpan ke database
    existing_orders = {row.question_order for row in rows}
    next_order = 1

    for question in selected_questions:
        while next_order in existing_orders:
            next_order += 1
        row = DailyMissionQuestion(
            tanggal=today,
            question_order=next_order,
            question_id=question.id,
            set_by_teacher=False,
        )
        db.session.add(row)
        rows.append(row)
        existing_orders.add(next_order)

    if rows:
        db.session.commit()

    return DailyMissionQuestion.query.filter_by(tanggal=today).order_by(DailyMissionQuestion.question_order.asc()).all()

def _build_static_image_url(raw_value):
    value = (raw_value or '').strip()
    if not value:
        return None
    lowered = value.lower()
    if lowered.startswith('color:'):
        return _build_visual_image_data(value.split(':', 1)[1], 'warna_bentuk')
    if lowered.startswith('shape:'):
        return _build_visual_image_data(value.split(':', 1)[1], 'warna_bentuk')
    if lowered.startswith('number:'):
        return _build_visual_image_data(value.split(':', 1)[1], 'angka')
    if lowered.startswith('letter:'):
        return _build_visual_image_data(value.split(':', 1)[1], 'huruf')
    if lowered.startswith('count:'):
        parts = value.split(':')
        count_value = 3
        count_label = 'benda'
        if len(parts) >= 2 and parts[1].strip():
            count_label = parts[1].strip()
        if len(parts) >= 3:
            try:
                count_value = max(1, min(30, int(parts[2])))
            except (TypeError, ValueError):
                count_value = 3
        return _count_objects_svg_data(count_value, count_label)
    if lowered.startswith('http://') or lowered.startswith('https://') or lowered.startswith('data:'):
        return value
    if lowered.startswith('/static/'):
        return value
    return url_for('static', filename=value.lstrip('/'))


def _svg_data_uri(svg_markup):
    return 'data:image/svg+xml;utf8,' + quote(svg_markup)


def _count_objects_svg_data(count, label='benda'):
    try:
        total = max(1, min(30, int(count)))
    except (TypeError, ValueError):
        total = 1

    columns = 5
    rows = max(1, (total + columns - 1) // columns)
    radius = 10 if total > 20 else 11 if total > 15 else 12
    gap_x = 36
    gap_y = 28 if rows >= 5 else 32
    start_x = 48
    start_y = 42
    dots = []

    for idx in range(total):
        col = idx % columns
        row = idx // columns
        cx = start_x + (col * gap_x)
        cy = start_y + (row * gap_y)
        dots.append("<circle cx='" + str(cx) + "' cy='" + str(cy) + "' r='" + str(radius) + "' fill='#ff8a65' stroke='#c94f2f' stroke-width='3'/>")
        dots.append("<line x1='" + str(cx) + "' y1='" + str(cy + radius) + "' x2='" + str(cx - 2) + "' y2='" + str(cy + radius + 14) + "' stroke='#7b8ba6' stroke-width='2'/>")

    safe_label = html.escape((label or 'benda')[:16])
    safe_total = html.escape(str(total))
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
        "<rect x='8' y='8' width='224' height='154' rx='20' fill='#fff5f0' stroke='#ffc09b' stroke-width='6'/>"
        + ''.join(dots) +
        "<text x='120' y='148' text-anchor='middle' font-family='Arial' font-size='18' font-weight='700' fill='#8a4f08'>" + safe_label + "</text>"
        "<text x='205' y='30' text-anchor='middle' font-family='Arial' font-size='18' font-weight='700' fill='#b85c38'>" + safe_total + "</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _shape_svg_markup(shape_name):
    if shape_name == 'bola':
        return "<circle cx='120' cy='88' r='56' fill='#67b8ff' stroke='#1b5f96' stroke-width='8'/><circle cx='97' cy='66' r='16' fill='#bfe2ff'/>"
    if shape_name == 'kubus':
        return "<polygon points='68,58 122,40 172,64 118,82' fill='#9dcbf7' stroke='#1b5f96' stroke-width='6'/><polygon points='68,58 68,120 118,146 118,82' fill='#77b4eb' stroke='#1b5f96' stroke-width='6'/><polygon points='118,82 172,64 172,126 118,146' fill='#5ea2df' stroke='#1b5f96' stroke-width='6'/>"
    if shape_name == 'balok':
        return "<polygon points='50,64 120,44 192,66 122,86' fill='#a8d2f3' stroke='#1b5f96' stroke-width='6'/><polygon points='50,64 50,122 122,148 122,86' fill='#7cb8e8' stroke='#1b5f96' stroke-width='6'/><polygon points='122,86 192,66 192,124 122,148' fill='#629ed7' stroke='#1b5f96' stroke-width='6'/>"
    if shape_name == 'tabung':
        return "<ellipse cx='120' cy='44' rx='56' ry='18' fill='#9ec8ee' stroke='#1b5f96' stroke-width='6'/><rect x='64' y='44' width='112' height='78' fill='#76b2e4' stroke='#1b5f96' stroke-width='6'/><ellipse cx='120' cy='122' rx='56' ry='18' fill='#5f9ed9' stroke='#1b5f96' stroke-width='6'/>"
    if shape_name == 'kerucut':
        return "<polygon points='120,28 58,128 182,128' fill='#80b8e9' stroke='#1b5f96' stroke-width='6'/><ellipse cx='120' cy='128' rx='62' ry='16' fill='#5f9ed9' stroke='#1b5f96' stroke-width='6'/>"
    if shape_name == 'limas':
        return "<polygon points='120,24 56,128 184,128' fill='#7ab1e4' stroke='#1b5f96' stroke-width='6'/><polygon points='120,24 120,128 184,128' fill='#5f9ed9' stroke='#1b5f96' stroke-width='6'/>"
    if shape_name == 'prisma':
        return "<polygon points='66,56 124,36 176,58 118,78' fill='#9dcaf0' stroke='#1b5f96' stroke-width='6'/><polygon points='66,56 66,120 118,146 118,78' fill='#79b5e6' stroke='#1b5f96' stroke-width='6'/><polygon points='118,78 176,58 176,122 118,146' fill='#5f9ed9' stroke='#1b5f96' stroke-width='6'/>"
    return "<rect x='60' y='44' width='120' height='92' rx='14' fill='#80b7e8' stroke='#1b5f96' stroke-width='6'/>"


def _build_visual_image_data(value, category_hint='umum'):
    token = (value or '').strip()
    token_lower = token.lower()
    category = (category_hint or '').strip().lower()

    if token_lower in COLOR_VISUAL_MAP:
        fill = COLOR_VISUAL_MAP[token_lower]
        stroke = '#37474f' if token_lower != 'putih' else '#90a4ae'
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
            "<rect x='14' y='14' width='212' height='142' rx='20' fill='" + fill + "' stroke='" + stroke + "' stroke-width='8'/>"
            "</svg>"
        )
        return _svg_data_uri(svg)

    if token_lower in SHAPE_VISUAL_SET or category == 'warna_bentuk':
        shape_markup = _shape_svg_markup(token_lower)
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
            "<rect x='0' y='0' width='240' height='170' rx='18' fill='#f4f9ff'/>"
            + shape_markup +
            "</svg>"
        )
        return _svg_data_uri(svg)

    if token.isdigit() and len(token) <= 2:
        safe = html.escape(token)
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
            "<rect x='10' y='10' width='220' height='150' rx='20' fill='#eef6ff' stroke='#8bb8e8' stroke-width='6'/>"
            "<text x='120' y='108' text-anchor='middle' font-size='88' font-weight='700' fill='#0f3a72' font-family='Arial'>" + safe + "</text>"
            "</svg>"
        )
        return _svg_data_uri(svg)

    display_text = token[:10] if token else '?'
    safe_text = html.escape(display_text)
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='170' viewBox='0 0 240 170'>"
        "<rect x='10' y='10' width='220' height='150' rx='20' fill='#fff7e8' stroke='#f2c482' stroke-width='6'/>"
        "<text x='120' y='104' text-anchor='middle' font-size='72' font-weight='700' fill='#8c4c08' font-family='Arial'>" + safe_text + "</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _rows_for_adventure_game(game_key):
    _seed_visual_questions_if_needed()

    if game_key == 'warna':
        rows = Soal.query.filter(Soal.kategori.in_(['warna', 'bentuk', 'warna_bentuk', 'bentuk_bangun_ruang'])).all()
    elif game_key == 'angka':
        rows = Soal.query.filter_by(kategori='angka').filter(~Soal.question_type.in_(['number_sequence', 'before_number'])).all()
    else:
        rows = Soal.query.filter_by(kategori=game_key).all()

    explicit_enabled = {
        row.question_id
        for row in QuestionUsage.query.filter_by(context='adventure_map', game_key=game_key, is_active=True).all()
    }
    explicit_scoped = {
        row.question_id
        for row in QuestionUsage.query.filter_by(context='adventure_map', game_key=game_key).all()
    }

    filtered = []
    for row in rows:
        if not _is_valid_adventure_answer_key(row.jawaban_benar):
            continue

        if row.id in explicit_enabled:
            filtered.append(row)
            continue
        if row.id in explicit_scoped:
            continue
        if row.use_in_adventure_map:
            filtered.append(row)
    return filtered


def _seed_visual_questions_if_needed():
    huruf_count = Soal.query.filter_by(kategori='huruf').count()
    angka_count = Soal.query.filter_by(kategori='angka').count()
    warna_count = Soal.query.filter_by(kategori='warna').count()
    bentuk_count = Soal.query.filter(Soal.kategori.in_(['bentuk', 'bentuk_bangun_ruang'])).count()

    to_insert = []

    if huruf_count < 80:
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        for cycle in range(3):
            for index, letter in enumerate(letters):
                prev_letter = letters[(index - 1) % len(letters)]
                next_letter = letters[(index + 1) % len(letters)]
                jump_letter = letters[(index + 5) % len(letters)]

                to_insert.append(Soal(
                    kategori='huruf',
                    difficulty='mudah' if cycle == 0 else 'sedang',
                    pertanyaan='Pilih huruf yang sesuai.',
                    pilihan_a=letter,
                    pilihan_b=next_letter,
                    pilihan_c=prev_letter,
                    pilihan_d=None,
                    jawaban_benar='A',
                    question_type='match_letter',
                    image_question=f'letter:{letter}',
                    use_in_daily_mission=True,
                    use_in_adventure_map=True,
                ))

                to_insert.append(Soal(
                    kategori='huruf',
                    difficulty='mudah' if cycle == 0 else 'sedang',
                    pertanyaan='Pilih kata yang diawali huruf yang benar.',
                    pilihan_a=f'{letter}a',
                    pilihan_b=f'{prev_letter}a',
                    pilihan_c=f'{jump_letter}a',
                    pilihan_d=None,
                    jawaban_benar='A',
                    question_type='initial_letter',
                    image_question=f'letter:{letter}',
                    use_in_daily_mission=True,
                    use_in_adventure_map=True,
                ))

                if len(to_insert) >= 120:
                    break
            if len(to_insert) >= 120:
                break

    if angka_count < 90:
        for number in range(1, 31):
            prev_num = 30 if number == 1 else number - 1
            next_num = 1 if number == 30 else number + 1
            jump_num = ((number + 6 - 1) % 30) + 1

            to_insert.append(Soal(
                kategori='angka',
                difficulty='mudah',
                pertanyaan='Hitung gambar lalu pilih angka.',
                pilihan_a=str(number),
                pilihan_b=str(prev_num),
                pilihan_c=str(next_num),
                pilihan_d=None,
                jawaban_benar='A',
                question_type='count_objects',
                image_question=f'count:balloon:{number}',
                use_in_daily_mission=True,
                use_in_adventure_map=True,
            ))
            to_insert.append(Soal(
                kategori='angka',
                difficulty='mudah',
                pertanyaan='Pilih angka yang benar.',
                pilihan_a=str(number),
                pilihan_b=str(jump_num),
                pilihan_c=str(prev_num),
                pilihan_d=None,
                jawaban_benar='A',
                question_type='match_number',
                image_question=f'number:{number}',
                use_in_daily_mission=True,
                use_in_adventure_map=True,
            ))

            if len(to_insert) >= 220:
                break

    if warna_count < 60:
        color_options = [
            ('merah', 'biru', 'hijau'),
            ('biru', 'kuning', 'merah'),
            ('kuning', 'ungu', 'hijau'),
            ('hijau', 'merah', 'oranye'),
            ('oranye', 'biru', 'hijau'),
            ('ungu', 'kuning', 'merah'),
            ('putih', 'hitam', 'abu-abu'),
            ('hitam', 'putih', 'cokelat'),
            ('cokelat', 'abu-abu', 'biru'),
            ('abu-abu', 'putih', 'merah'),
        ]
        for color, w1, w2 in color_options:
            for _ in range(3):
                to_insert.append(Soal(
                    kategori='warna',
                    difficulty='mudah',
                    pertanyaan='Pilih warna yang sesuai gambar.',
                    pilihan_a=color,
                    pilihan_b=w1,
                    pilihan_c=w2,
                    pilihan_d=None,
                    jawaban_benar='A',
                    question_type='match_color',
                    image_question=f'color:{color}',
                    use_in_daily_mission=True,
                    use_in_adventure_map=True,
                ))

    if bentuk_count < 60:
        shape_options = [
            ('bola', 'kubus', 'limas'),
            ('kubus', 'balok', 'bola'),
            ('balok', 'tabung', 'kubus'),
            ('tabung', 'kerucut', 'bola'),
            ('kerucut', 'limas', 'tabung'),
            ('limas', 'prisma', 'bola'),
            ('prisma', 'limas', 'kerucut'),
        ]
        for shape, w1, w2 in shape_options:
            for _ in range(4):
                to_insert.append(Soal(
                    kategori='bentuk_bangun_ruang',
                    difficulty='mudah',
                    pertanyaan='Pilih bangun ruang yang sesuai gambar.',
                    pilihan_a=shape,
                    pilihan_b=w1,
                    pilihan_c=w2,
                    pilihan_d=None,
                    jawaban_benar='A',
                    question_type='match_shape',
                    image_question=f'shape:{shape}',
                    use_in_daily_mission=True,
                    use_in_adventure_map=True,
                ))

    if to_insert:
        db.session.add_all(to_insert)
        db.session.flush()

        for row in to_insert:
            _set_question_usages(
                question_id=row.id,
                include_daily_mission=bool(row.use_in_daily_mission),
                include_adventure_map=bool(row.use_in_adventure_map),
                category=row.kategori,
            )

        db.session.commit()


def _prompt_for_game(game_key):
    if game_key == 'huruf':
        return 'Pilih huruf yang sesuai gambar.'
    if game_key == 'angka':
        return 'Pilih angka yang sesuai gambar.'
    return 'Pilih jawaban yang sesuai gambar.'


def _build_daily_questions_from_db(game_key, level_rules):
    rows = _rows_for_adventure_game(game_key)
    if not rows:
        return []

    total_needed = sum(rule['question_count'] for rule in level_rules)
    today_seed = f"{game_key}-{date.today().isoformat()}-db-v2"
    day_rng = random.Random(today_seed)

    row_pool = list(rows)
    day_rng.shuffle(row_pool)
    selected_rows = [row_pool[index % len(row_pool)] for index in range(total_needed)]

    result = []
    pointer = 0
    global_index = 0
    for rule in level_rules:
        level = rule['level']
        count = rule['question_count']
        level_rows = selected_rows[pointer:pointer + count]
        pointer += count

        for number, row in enumerate(level_rows, start=1):
            answer_letter = Soal.answer_key_to_letter(row.jawaban_benar)
            option_map = {
                'A': (row.pilihan_a or '').strip(),
                'B': (row.pilihan_b or '').strip(),
                'C': (row.pilihan_c or '').strip(),
                'D': (row.pilihan_d or '').strip(),
            }
            options = [value for value in [option_map['A'], option_map['B'], option_map['C'], option_map['D']] if value]
            options = list(dict.fromkeys(options))
            if not options:
                continue

            answer_text = option_map.get(answer_letter) or options[0]
            if answer_text not in options:
                options.insert(0, answer_text)

            option_rng = random.Random(f"{today_seed}-{row.id}-{global_index}")
            option_rng.shuffle(options)

            question_image = _build_static_image_url(row.image_question)
            if not question_image:
                question_image = _build_visual_image_data(answer_text, row.kategori)

            option_image_map_raw = {
                option_map['A']: _build_static_image_url(row.image_option_a),
                option_map['B']: _build_static_image_url(row.image_option_b),
                option_map['C']: _build_static_image_url(row.image_option_c),
                option_map['D']: _build_static_image_url(row.image_option_d),
            }
            option_images = {}
            for option_value in options:
                image_value = option_image_map_raw.get(option_value)
                if not image_value:
                    image_value = _build_visual_image_data(option_value, row.kategori)
                option_images[option_value] = image_value

            result.append({
                'question_id': f"db-{row.id}-{global_index}",
                'display': answer_text,
                'display_value': answer_text,
                'prompt': _prompt_for_game(game_key),
                'options': options,
                'option_images': option_images,
                'question_image': question_image,
                'answer': answer_text,
                'level': level,
                'number_in_level': number,
                'time_limit': rule['time_limit'],
                'weight': rule['weight']
            })
            global_index += 1

    return result


def normalize_account_role(role):
    normalized = (role or '').strip().lower()
    if normalized in ['orang_tua', 'orangtua']:
        return 'orang_tua'
    if normalized in STUDENT_ROLES:
        return 'murid'
    return normalized


def get_role_display_name(role):
    normalized = normalize_account_role(role)
    if normalized == 'orang_tua':
        return 'Orang Tua'
    if normalized == 'murid':
        return 'Murid'
    if normalized == 'guru':
        return 'Guru'
    if normalized == 'admin':
        return 'Admin'
    return normalized.replace('_', ' ').title() or '-'


def generate_reset_password(length=8):
    length = max(8, int(length or 8))
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(2))
    digits = ''.join(secrets.choice(string.digits) for _ in range(length - 3))
    raw = list(uppercase + lowercase + digits)
    secrets.SystemRandom().shuffle(raw)
    return ''.join(raw)


def get_access_time_setting(create_if_missing=True):
    setting = AccessTime.query.order_by(AccessTime.id.asc()).first()
    if setting or not create_if_missing:
        return setting

    setting = AccessTime(start_time=DEFAULT_ACCESS_START, end_time=DEFAULT_ACCESS_END)
    db.session.add(setting)
    db.session.commit()
    return setting


def get_daily_mission_access_time_setting(create_if_missing=True):
    setting = DailyMissionAccessTime.query.order_by(DailyMissionAccessTime.id.asc()).first()
    if setting or not create_if_missing:
        return setting

    setting = DailyMissionAccessTime(
        start_time=DEFAULT_DAILY_MISSION_ACCESS_START,
        end_time=DEFAULT_DAILY_MISSION_ACCESS_END,
    )
    db.session.add(setting)
    db.session.commit()
    return setting


def get_student_menu_access_time_setting(create_if_missing=True):
    setting = StudentMenuAccessTime.query.order_by(StudentMenuAccessTime.id.asc()).first()
    if setting or not create_if_missing:
        return setting

    setting = StudentMenuAccessTime(
        start_time=DEFAULT_MENU_ACCESS_START,
        end_time=DEFAULT_MENU_ACCESS_END,
    )
    db.session.add(setting)
    db.session.commit()
    return setting


def get_daily_mission_access_status(now_dt=None):
    now_dt = now_dt or datetime.now()
    # Ensure now_dt is datetime, not date
    if isinstance(now_dt, date) and not isinstance(now_dt, datetime):
        now_dt = datetime.combine(now_dt, datetime.min.time())
    setting = get_daily_mission_access_time_setting(create_if_missing=True)
    start = setting.start_time if setting else DEFAULT_DAILY_MISSION_ACCESS_START
    end = setting.end_time if setting else DEFAULT_DAILY_MISSION_ACCESS_END
    now_time = now_dt.time()

    # Daily mission window is validated as start < end.
    allowed_now = start <= now_time <= end if start and end else True

    status_label = 'tersedia'
    status_message = f"Misi tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}."
    if not allowed_now:
        if now_time < start:
            status_label = 'belum'
            status_message = f"Misi belum tersedia. Misi tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}."
        else:
            status_label = 'ditutup'
            status_message = f"Misi sudah ditutup. Misi tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}."

    return {
        'allowed_now': allowed_now,
        'start': start,
        'end': end,
        'status_label': status_label,
        'status_message': status_message,
    }


def is_student_role(role):
    return (role or '').strip().lower() in STUDENT_ROLES


def is_now_in_access_window(now_dt=None):
    now_dt = now_dt or datetime.now()
    setting = get_access_time_setting(create_if_missing=True)
    start = setting.start_time if setting else DEFAULT_ACCESS_START
    end = setting.end_time if setting else DEFAULT_ACCESS_END
    now_time = now_dt.time()

    # Support overnight windows, e.g. 22:00 - 05:00.
    if start <= end:
        allowed = start <= now_time <= end
    else:
        allowed = now_time >= start or now_time <= end

    return allowed, start, end


def get_access_status_for_user(user_obj):
    allowed_now, start, end = is_now_in_access_window()

    if not is_student_role(getattr(user_obj, 'role', '')):
        return {
            'is_limited': False,
            'allowed_now': True,
            'start': start,
            'end': end,
            'message': f'Peta Petualangan tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}.',
            'status_label': 'tersedia',
        }

    now_time = datetime.now().time()
    if allowed_now:
        message = f'Peta Petualangan tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}.'
        status_label = 'tersedia'
    elif now_time < start:
        message = f'Peta Petualangan belum tersedia. Peta tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}.'
        status_label = 'belum'
    else:
        message = f'Peta Petualangan sudah ditutup. Peta tersedia pukul {format_hhmm(start)} - {format_hhmm(end)}.'
        status_label = 'ditutup'

    return {
        'is_limited': True,
        'allowed_now': allowed_now,
        'start': start,
        'end': end,
        'message': message,
        'status_label': status_label,
    }


def enforce_game_access_time_or_redirect():
    status = get_access_status_for_user(current_user)
    if status['is_limited'] and not status['allowed_now']:
        flash('Game hanya bisa dimainkan pada jam yang telah ditentukan oleh guru.', 'warning')
        return redirect(url_for('main.peta_pertualangan'))
    return None


def normalize_game_key(game_key):
    key = (game_key or '').strip().lower()
    if key in ['warna-bentuk', 'warna_bentuk']:
        return 'warna'
    return key


def find_today_gameplay(user_id, game_key):
    return GamePlay.query.filter_by(
        user_id=user_id,
        game_name=game_key,
        played_date=date.today()
    ).first()


def find_any_gameplay(user_id, game_key):
    return GamePlay.query.filter_by(
        user_id=user_id,
        game_name=game_key
    ).first()


def get_or_create_progress(user_id, game_key):
    progress = UserProgress.query.filter_by(user_id=user_id, game_id=game_key).first()
    if not progress:
        progress = UserProgress(user_id=user_id, game_id=game_key, status='belum')
        db.session.add(progress)
    return progress


def set_progress_status(user_id, game_key, status):
    if game_key not in ADVENTURE_GAMES:
        return

    progress = get_or_create_progress(user_id, game_key)

    if progress.status == 'selesai':
        return

    progress.status = status
    progress.tanggal_update = datetime.utcnow()


def get_user_adventure_progress(user_id):
    rows = UserProgress.query.filter_by(user_id=user_id).all()
    row_map = {row.game_id: row for row in rows}

    changed = False
    progress_map = {}

    for key in ADVENTURE_GAMES:
        row = row_map.get(key)
        if not row:
            row = UserProgress(user_id=user_id, game_id=key, status='belum')
            db.session.add(row)
            row_map[key] = row
            changed = True

        if row.status != 'selesai' and find_any_gameplay(user_id, key):
            row.status = 'selesai'
            row.tanggal_update = datetime.utcnow()
            changed = True

        progress_map[key] = {
            'status': row.status,
            'tanggal_update': row.tanggal_update.isoformat() if row.tanggal_update else None
        }

    if changed:
        db.session.commit()

    return progress_map


def get_or_create_game_history(user_id, game_key, tanggal=None):
    tanggal = tanggal or date.today()
    history = UserGameHistory.query.filter_by(
        user_id=user_id,
        game_id=game_key,
        tanggal_main=tanggal
    ).first()
    if not history:
        history = UserGameHistory(
            user_id=user_id,
            game_id=game_key,
            tanggal_main=tanggal,
            status='belum',
            answered_questions=0,
            total_questions=0,
            skor=0,
            updated_at=datetime.utcnow()
        )
        db.session.add(history)
    return history


def start_game_history(user_id, game_key, total_questions):
    history = get_or_create_game_history(user_id, game_key)
    if history.status != 'selesai':
        history.status = 'sedang'
    history.total_questions = max(int(total_questions or 0), history.total_questions or 0)
    history.updated_at = datetime.utcnow()


def update_game_history_progress(user_id, game_key, answered_questions=None, total_questions=None, status=None):
    history = get_or_create_game_history(user_id, game_key)
    if answered_questions is not None:
        try:
            answered = max(0, int(answered_questions))
        except (TypeError, ValueError):
            answered = history.answered_questions or 0
        history.answered_questions = max(history.answered_questions or 0, answered)

    if total_questions is not None:
        try:
            total = max(0, int(total_questions))
        except (TypeError, ValueError):
            total = history.total_questions or 0
        history.total_questions = max(history.total_questions or 0, total)

    if status in ['belum', 'sedang', 'selesai']:
        if history.status != 'selesai' or status == 'selesai':
            history.status = status

    history.updated_at = datetime.utcnow()


def complete_game_history(user_id, game_key, total_questions, score):
    history = get_or_create_game_history(user_id, game_key)
    total = max(0, int(total_questions or 0))
    history.total_questions = total
    history.answered_questions = total
    history.status = 'selesai'
    history.skor = max(0, int(score or 0))
    history.updated_at = datetime.utcnow()


def grant_daily_login_star(user_id):
    today = date.today()
    existing = UserDailyLogin.query.filter_by(user_id=user_id, tanggal=today).first()
    if existing:
        return False

    db.session.add(UserDailyLogin(
        user_id=user_id,
        tanggal=today,
        bintang_didapat=True,
        created_at=datetime.utcnow()
    ))
    return True


def get_or_create_user_daily_status(user_id, target_date=None):
    target_date = target_date or date.today()
    daily_status = UserDailyStatus.query.filter_by(user_id=user_id, date=target_date).first()
    if not daily_status:
        daily_status = UserDailyStatus(user_id=user_id, date=target_date)
        db.session.add(daily_status)
    return daily_status


def get_today_mission_completion(user_id, target_date=None):
    target_date = target_date or date.today()
    progress = ProgresHarian.query.filter_by(user_id=user_id, tanggal=target_date).first()
    mission_run = DailyMissionRun.query.filter_by(user_id=user_id, tanggal=target_date).first()
    return bool(
        (progress and progress.status_selesai) or
        (mission_run and mission_run.status_selesai)
    )


def sync_user_daily_status(user_id, target_date=None):
    target_date = target_date or date.today()
    daily_status = get_or_create_user_daily_status(user_id, target_date)
    daily_status.mission_completed = get_today_mission_completion(user_id, target_date)
    return daily_status


def get_total_stars(user_id):
    return UserDailyLogin.query.filter_by(user_id=user_id, bintang_didapat=True).count()


def sync_user_level_from_completed_games(user_obj):
    completed_games = UserProgress.query.filter_by(user_id=user_obj.id, status='selesai').count()
    level = min(3, max(0, completed_games))
    if user_obj.level != level:
        user_obj.level = level
        db.session.add(user_obj)
    return level


def ensure_day6_certificate(user_obj):
    login_days = UserDailyLogin.query.filter_by(user_id=user_obj.id, bintang_didapat=True).count()
    if login_days < 6:
        return None

    existing = UserCertificate.query.filter_by(user_id=user_obj.id, certificate_type='Milestone Hari Ke-6').first()
    if existing:
        return existing

    total_score = int(
        db.session.query(func.coalesce(func.sum(UserScore.skor), 0))
        .filter(UserScore.user_id == user_obj.id)
        .scalar() or 0
    )
    cert = UserCertificate(
        user_id=user_obj.id,
        issue_date=date.today(),
        certificate_type='Milestone Hari Ke-6',
        score_snapshot=total_score,
        message='Selamat! Kamu konsisten belajar hingga hari ke-6.'
    )
    db.session.add(cert)
    return cert


def build_daily_leaderboard(today):
    completed_users_subquery = (
        db.session.query(UserGameHistory.user_id)
        .filter(UserGameHistory.tanggal_main == today, UserGameHistory.status == 'selesai')
        .distinct()
        .subquery()
    )

    rows = (
        db.session.query(
            User.id.label('user_id'),
            User.username.label('username'),
            func.coalesce(func.sum(UserScore.skor), 0).label('daily_score')
        )
        .join(UserScore, UserScore.user_id == User.id)
        .filter(User.id.in_(db.session.query(completed_users_subquery.c.user_id)))
        .filter(UserScore.tanggal == today)
        .group_by(User.id, User.username)
        .order_by(func.coalesce(func.sum(UserScore.skor), 0).desc(), User.username.asc())
        .all()
    )

    result = []
    for idx, row in enumerate(rows, start=1):
        result.append({
            'rank': idx,
            'user_id': row.user_id,
            'username': (row.username or '').strip() or 'Belum ada',
            'score': int(row.daily_score or 0)
        })
    return result


def build_certificate_svg(user_obj, certificate_obj):
    safe_name = (user_obj.name or user_obj.username or 'Murid').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    safe_message = (certificate_obj.message or 'Selamat atas pencapaianmu!').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return f"""
<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='850' viewBox='0 0 1200 850'>
  <defs>
    <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
      <stop offset='0%' stop-color='#fdf5d8'/>
      <stop offset='100%' stop-color='#e0f3ff'/>
    </linearGradient>
  </defs>
  <rect x='0' y='0' width='1200' height='850' fill='url(#bg)'/>
  <rect x='40' y='40' width='1120' height='770' fill='none' stroke='#1e4f86' stroke-width='8'/>
  <text x='600' y='160' text-anchor='middle' font-family='Arial' font-size='62' fill='#173c6b' font-weight='700'>SERTIFIKAT PENCAPAIAN</text>
  <text x='600' y='250' text-anchor='middle' font-family='Arial' font-size='34' fill='#2a2a2a'>Diberikan kepada:</text>
  <text x='600' y='330' text-anchor='middle' font-family='Arial' font-size='64' fill='#0f3a72' font-weight='700'>{safe_name}</text>
  <text x='600' y='410' text-anchor='middle' font-family='Arial' font-size='32' fill='#2a2a2a'>{safe_message}</text>
  <text x='600' y='480' text-anchor='middle' font-family='Arial' font-size='30' fill='#2a2a2a'>Skor: {certificate_obj.score_snapshot}</text>
  <text x='600' y='540' text-anchor='middle' font-family='Arial' font-size='30' fill='#2a2a2a'>Jenis: {certificate_obj.certificate_type}</text>
  <text x='600' y='600' text-anchor='middle' font-family='Arial' font-size='28' fill='#2a2a2a'>Tanggal: {certificate_obj.issue_date.isoformat()}</text>
  <text x='600' y='710' text-anchor='middle' font-family='Arial' font-size='26' fill='#1e4f86'>Gamifikasi PAUD</text>
</svg>
""".strip()


def get_certificate_name(rank):
    if rank == 1:
        return 'Sertifikat Emas'
    if rank == 2:
        return 'Sertifikat Perak'
    if rank == 3:
        return 'Sertifikat Perunggu'
    return 'Sertifikat Partisipasi'


def normalize_mission_category(raw_category):
    key = (raw_category or '').strip().lower()
    return MISSION_CATEGORY_ALIASES.get(key)


def get_audio_file_record(name):
    normalized_name = (name or '').strip().lower()
    if not normalized_name:
        return None
    return AudioFile.query.filter_by(name=normalized_name).first()


def resolve_audio_storage(record):
    if not record:
        return None, None, 'record tidak ditemukan'

    if record.file_blob:
        mime_type = 'audio/mpeg'
        return io.BytesIO(record.file_blob), mime_type, None

    relative_path = (record.file_path or '').strip().replace('\\', '/')
    if not relative_path:
        return None, None, 'file_path kosong'

    absolute_path = os.path.abspath(os.path.join(current_app.static_folder, relative_path))
    static_root = os.path.abspath(current_app.static_folder)
    if not absolute_path.startswith(static_root):
        return None, None, 'path audio tidak valid'
    if not os.path.exists(absolute_path):
        return None, None, f'file audio tidak ditemukan: {absolute_path}'

    mime_type = mimetypes.guess_type(absolute_path)[0] or 'audio/mpeg'
    return absolute_path, mime_type, None


def get_daily_mission_questions(user_id, today):
    rows = get_or_generate_daily_mission_rows(today)
    if not rows:
        return []

    mapped_ids = [row.question_id for row in rows if row.question_id]
    question_map = _get_soal_by_ids(mapped_ids)

    result = []
    changed = False
    fallback_candidates = [
        q for q in Soal.query.all()
        if normalize_mission_category(q.kategori)
    ]

    # Jika tidak ada soal dengan kategori misi yang cocok, gunakan semua soal
    # sebagai fallback agar murid tetap dapat mengerjakan misi.
    if not fallback_candidates:
        fallback_candidates = list(Soal.query.all())
        # Tidak semua soal memiliki kategori misi; beri info debug singkat.
        print(f"[DEBUG] Tidak ada soal dengan kategori misi cocok; menggunakan semua soal sebagai fallback ({len(fallback_candidates)} soal)")

    for slot in rows:
        question = question_map.get(slot.question_id)
        if not question and fallback_candidates:
            question = random.choice(fallback_candidates)
            slot.question_id = question.id
            slot.set_by_teacher = False
            changed = True

        if question:
            result.append(question)

    if changed:
        db.session.commit()

    return result


def build_leaderboard_entries(limit=None):
    total_score_expr = func.coalesce(func.sum(GamePlay.score), 0)
    games_completed_expr = func.count(GamePlay.id)
    first_completed_expr = func.min(GamePlay.played_at)

    rows = (
        db.session.query(
            User.id.label('user_id'),
            User.username.label('username'),
            User.name.label('name'),
            total_score_expr.label('total_score'),
            games_completed_expr.label('games_completed'),
            first_completed_expr.label('first_completed_at')
        )
        .outerjoin(GamePlay, GamePlay.user_id == User.id)
        .filter(func.lower(User.role).in_(STUDENT_ROLES))
        .group_by(User.id, User.username, User.name)
        .order_by(
            total_score_expr.desc(),
            games_completed_expr.desc(),
            case((first_completed_expr.is_(None), 1), else_=0).asc(),
            first_completed_expr.asc(),
            User.username.asc()
        )
    )

    if limit is not None:
        rows = rows.limit(limit)

    leaderboard_entries = []
    for rank, row in enumerate(rows.all(), start=1):
        username = (row.username or '').strip() or 'Belum ada'
        display_name = (row.name or '').strip() or username
        total_score = int(row.total_score or 0)
        games_completed = int(row.games_completed or 0)

        leaderboard_entries.append({
            'rank': rank,
            'user_id': row.user_id,
            'username': username,
            'name': display_name,
            'total_score': total_score,
            'games_completed': games_completed,
            'certificate': get_certificate_name(rank),
            'first_completed_at': row.first_completed_at
        })

    return leaderboard_entries


@main.route('/audio-db/<audio_name>')
@login_required
def audio_db_stream(audio_name):
    record = get_audio_file_record(audio_name)
    source, mime_type, error_message = resolve_audio_storage(record)
    if error_message:
        current_app.logger.error('Gagal memuat audio %s: %s', audio_name, error_message)
        abort(404)

    current_app.logger.info('Audio stream siap: name=%s, mime=%s, source=%s', audio_name, mime_type, 'blob' if getattr(record, 'file_blob', None) else (record.file_path if record else 'none'))

    if hasattr(source, 'read'):
        response = send_file(source, mimetype=mime_type, download_name=f'{audio_name}.mp3')
    else:
        response = send_file(source, mimetype=mime_type, conditional=True)

    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


@main.route('/api/audio-db/<audio_name>')
@login_required
def audio_db_metadata(audio_name):
    record = get_audio_file_record(audio_name)
    source, mime_type, error_message = resolve_audio_storage(record)
    return jsonify({
        'name': audio_name,
        'available': error_message is None,
        'mime_type': mime_type,
        'uses_blob': bool(record.file_blob) if record else False,
        'file_path': record.file_path if record else None,
        'stream_url': url_for('main.audio_db_stream', audio_name=audio_name),
        'error': error_message,
    })


@main.route('/api/user-daily-status')
@login_required
def api_user_daily_status():
    today = date.today()
    daily_status = sync_user_daily_status(current_user.id, today)
    db.session.commit()
    return jsonify({
        'user_id': current_user.id,
        'date': today.isoformat(),
        'mission_completed': bool(daily_status.mission_completed),
        'reminder_played': bool(daily_status.reminder_played),
        'completion_audio_played': bool(daily_status.completion_audio_played),
    })


@main.route('/api/user-daily-status/audio-played', methods=['POST'])
@login_required
def api_user_daily_status_audio_played():
    today = date.today()
    daily_status = sync_user_daily_status(current_user.id, today)
    payload = request.get_json() or {}
    audio_type = (payload.get('audio_type') or '').strip().lower()

    if audio_type == 'reminder':
        daily_status.reminder_played = True
    elif audio_type == 'completion':
        daily_status.mission_completed = True
        daily_status.completion_audio_played = True
    else:
        return jsonify({'message': 'audio_type tidak valid'}), 400

    db.session.commit()
    return jsonify({
        'message': 'Status audio diperbarui.',
        'user_id': current_user.id,
        'date': today.isoformat(),
        'mission_completed': bool(daily_status.mission_completed),
        'reminder_played': bool(daily_status.reminder_played),
        'completion_audio_played': bool(daily_status.completion_audio_played),
    })


def build_top_five_slots(entries):
    slots = []
    for position in range(1, 6):
        entry = next((item for item in entries if item['rank'] == position), None)
        if entry:
            slots.append(entry)
            continue

        slots.append({
            'rank': position,
            'user_id': None,
            'username': 'Belum ada',
            'name': 'Belum ada',
            'total_score': 0,
            'games_completed': 0,
            'certificate': get_certificate_name(position),
            'first_completed_at': None
        })

    return slots


def build_huruf_question_bank():
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    bank = []

    for index, letter in enumerate(letters):
        n1 = letters[(index + 1) % len(letters)]
        n2 = letters[(index + 2) % len(letters)]
        p1 = letters[(index - 1) % len(letters)]
        p2 = letters[(index - 2) % len(letters)]

        bank.append({
            'id': f'up-{letter}',
            'display': letter,
            'prompt': 'Tebak huruf ini.',
            'options': [letter, n1, n2, p1],
            'answer': letter
        })

        lower = letter.lower()
        bank.append({
            'id': f'low-{letter}',
            'display': lower,
            'prompt': 'Tebak huruf ini.',
            'options': [lower, p1.lower(), n1.lower(), p2.lower()],
            'answer': lower
        })

    return bank


def get_daily_huruf_questions():
    bank = build_huruf_question_bank()
    total_needed = sum(rule['question_count'] for rule in HURUF_LEVEL_RULES)
    today_seed = f"huruf-{date.today().isoformat()}"
    rng = random.Random(today_seed)
    rng.shuffle(bank)

    selected = bank[:total_needed]
    questions = []
    pointer = 0

    for rule in HURUF_LEVEL_RULES:
        for number_in_level in range(1, rule['question_count'] + 1):
            item = selected[pointer]
            pointer += 1

            options = list(item['options'])
            option_rng = random.Random(f"{today_seed}-{item['id']}")
            option_rng.shuffle(options)

            questions.append({
                'question_id': f"letter-{item['id']}",
                'display': item['display'],
                'display_value': item['display'],
                'prompt': item['prompt'],
                'options': options,
                'option_images': {},
                'question_image': None,
                'answer': item['answer'],
                'level': rule['level'],
                'number_in_level': number_in_level,
                'time_limit': rule['time_limit'],
                'weight': rule['weight']
            })

    return questions


def get_daily_huruf_questions_public():
    questions = []
    for item in get_daily_huruf_questions():
        questions.append({
            'question_id': item['question_id'],
            'display': item['display'],
            'prompt': item['prompt'],
            'options': item['options'],
            'question_image': item.get('question_image'),
            'option_images': item.get('option_images', {}),
            'level': item['level'],
            'number_in_level': item['number_in_level'],
            'time_limit': item['time_limit'],
            'weight': item['weight']
        })
    return questions


def find_huruf_question(question_id):
    questions = get_daily_huruf_questions()
    return next((item for item in questions if item['question_id'] == question_id), None)


def build_angka_question_bank():
    bank = []

    for number in range(1, 31):
        prev_num = 30 if number == 1 else number - 1
        next_num = 1 if number == 30 else number + 1
        far_num = ((number + 6 - 1) % 30) + 1

        bank.append({
            'id': f'num-{number}',
            'display': str(number),
            'prompt': f'Angka berapa ini: {number}?',
            'options': [str(number), str(prev_num), str(next_num)],
            'answer': str(number)
        })

        word_label = NUMBER_WORDS_ID.get(number, str(number))
        bank.append({
            'id': f'word-{number}',
            'display': word_label,
            'prompt': f'Bilangan "{word_label}" adalah angka berapa?',
            'options': [str(number), str(next_num), str(far_num)],
            'answer': str(number)
        })

        if number <= 15:
            objects = ' '.join(['o' for _ in range(number)])
            bank.append({
                'id': f'obj-{number}',
                'display': objects,
                'prompt': 'Hitung jumlah benda lalu pilih angkanya.',
                'options': [str(number), str(prev_num), str(next_num)],
                'answer': str(number)
            })

    return bank


def get_daily_angka_questions():
    return get_fixed_adventure_questions('angka', ANGKA_LEVEL_RULES)


def get_daily_angka_questions_public():
    questions = []
    for item in get_daily_angka_questions():
        questions.append({
            'question_id': item['question_id'],
            'display': item['display'],
            'prompt': item['prompt'],
            'options': item['options'],
            'question_image': item.get('question_image'),
            'option_images': item.get('option_images', {}),
            'level': item['level'],
            'number_in_level': item['number_in_level'],
            'time_limit': item['time_limit'],
            'weight': item['weight']
        })
    return questions


def find_angka_question(question_id):
    questions = get_daily_angka_questions()
    return next((item for item in questions if item['question_id'] == question_id), None)


def build_warna_bentuk_question_bank():
    bank = []

    color_items = [
        {'name': 'Merah', 'distractors': ['Biru', 'Hijau', 'Kuning']},
        {'name': 'Biru', 'distractors': ['Kuning', 'Merah', 'Hijau']},
        {'name': 'Kuning', 'distractors': ['Ungu', 'Biru', 'Oranye']},
        {'name': 'Hijau', 'distractors': ['Merah', 'Oranye', 'Biru']},
        {'name': 'Oranye', 'distractors': ['Hijau', 'Biru', 'Kuning']},
        {'name': 'Ungu', 'distractors': ['Kuning', 'Merah', 'Abu-abu']},
        {'name': 'Putih', 'distractors': ['Hitam', 'Abu-abu', 'Biru']},
        {'name': 'Hitam', 'distractors': ['Putih', 'Cokelat', 'Ungu']},
        {'name': 'Cokelat', 'distractors': ['Abu-abu', 'Biru', 'Hijau']},
        {'name': 'Abu-abu', 'distractors': ['Putih', 'Merah', 'Hitam']},
    ]

    shape_items = [
        {'name': 'Bola', 'feature': 'tidak punya sudut', 'distractors': ['Kubus', 'Limas', 'Kerucut']},
        {'name': 'Kubus', 'feature': '6 sisi sama besar', 'distractors': ['Balok', 'Tabung', 'Bola']},
        {'name': 'Balok', 'feature': '6 sisi, ada sisi panjang dan lebar', 'distractors': ['Kubus', 'Bola', 'Tabung']},
        {'name': 'Tabung', 'feature': 'alas dan tutup berbentuk lingkaran', 'distractors': ['Kerucut', 'Balok', 'Prisma']},
        {'name': 'Kerucut', 'feature': 'punya satu puncak', 'distractors': ['Tabung', 'Bola', 'Limas']},
        {'name': 'Limas', 'feature': 'punya puncak dan sisi segitiga', 'distractors': ['Prisma', 'Bola', 'Kerucut']},
        {'name': 'Prisma', 'feature': 'memiliki dua sisi alas sejajar', 'distractors': ['Limas', 'Kerucut', 'Tabung']},
    ]

    for item in color_items:
        all_options = [item['name']] + item['distractors']

        # Gambar warna -> pilih nama
        bank.append({
            'id': f"color-image-to-name-{item['name'].lower()}",
            'prompt': 'Warna apakah ini?',
            'display_kind': 'color',
            'display_value': item['name'],
            'option_mode': 'text',
            'options': all_options,
            'answer': item['name']
        })

        # Nama warna -> pilih gambar warna
        bank.append({
            'id': f"color-name-to-image-{item['name'].lower()}",
            'prompt': f"Pilih gambar warna untuk: {item['name']}",
            'display_kind': 'text',
            'display_value': item['name'],
            'option_mode': 'color_visual',
            'options': all_options,
            'answer': item['name']
        })

    for item in shape_items:
        all_options = [item['name']] + item['distractors']

        # Gambar bentuk -> pilih nama
        bank.append({
            'id': f"shape-image-to-name-{item['name'].lower()}",
            'prompt': 'Ini gambar bangun ruang apa?',
            'display_kind': 'shape',
            'display_value': item['name'],
            'option_mode': 'text',
            'options': all_options,
            'answer': item['name']
        })

        # Nama/ciri bentuk -> pilih gambar bentuk
        bank.append({
            'id': f"shape-feature-to-image-{item['name'].lower()}",
            'prompt': f"Bangun ruang dengan ciri '{item['feature']}' adalah...",
            'display_kind': 'text',
            'display_value': item['feature'],
            'option_mode': 'shape_visual',
            'options': all_options,
            'answer': item['name']
        })

    return bank


def get_daily_warna_bentuk_questions():
    return get_fixed_adventure_questions('warna', WARNA_BENTUK_LEVEL_RULES)


def get_daily_warna_bentuk_questions_public():
    questions = []
    for item in get_daily_warna_bentuk_questions():
        questions.append({
            'question_id': item['question_id'],
            'prompt': item['prompt'],
            'display_kind': item.get('display_kind', 'image'),
            'display_value': item.get('display_value', item.get('display')),
            'option_mode': item.get('option_mode', 'image_visual'),
            'options': item['options'],
            'question_image': item.get('question_image'),
            'option_images': item.get('option_images', {}),
            'level': item['level'],
            'number_in_level': item['number_in_level'],
            'time_limit': item['time_limit'],
            'weight': item['weight']
        })
    return questions


def find_warna_bentuk_question(question_id):
    questions = get_daily_warna_bentuk_questions()
    return next((item for item in questions if item['question_id'] == question_id), None)

# Halaman Utama (Landing page bila belum login, dashboard bila sudah login)
@main.route('/')
def index():
    if not current_user.is_authenticated:
        mascot_awal_path = os.path.join(current_app.static_folder, 'animations', 'mascot_awal.json')
        home_mascot_version = int(os.path.getmtime(mascot_awal_path)) if os.path.exists(mascot_awal_path) else int(datetime.utcnow().timestamp())
        return render_template('home.html', home_mascot_version=home_mascot_version)

    # Redirect berdasarkan role user yang sudah login
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == 'guru':
        return redirect(url_for('main.guru_dashboard'))
    elif current_user.role == 'orangtua':
        return redirect(url_for('main.orangtua_dashboard'))
    else:
        # Untuk murid dan role lainnya, arahkan ke menu
        return redirect(url_for('main.menu'))

# Admin Dashboard
@main.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied! Only Game Masters allowed.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.filter_by(role='user').all()
    return render_template('admin_dashboard.html', users=users)

# Give XP (Admin only)
@main.route('/give_xp/<int:user_id>', methods=['POST'])
@login_required
def give_xp(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    xp_amount = int(request.form.get('xp_amount', 0))
    user = User.query.get_or_404(user_id)
    
    user.xp += xp_amount
    # Simple Level Up Logic: Level up every 100 XP
    user.level = 1 + (user.xp // 100)
    
    db.session.commit()
    flash(f'Gave {xp_amount} XP to {user.name}. They are now Level {user.level}!', 'success')
    return redirect(url_for('main.admin_dashboard'))

# User Dashboard (Leaderboard included)
@main.route('/leaderboard')
@login_required
def leaderboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    # Leaderboard bisa diakses langsung, tapi bukan halaman utama
    leaderboard_entries = build_leaderboard_entries()
    leaderboard_top5 = build_top_five_slots(leaderboard_entries)

    current_user_entry = next(
        (entry for entry in leaderboard_entries if entry['user_id'] == current_user.id),
        None
    )

    if current_user_entry is None:
        fallback_rank = len(leaderboard_entries) + 1
        current_user_entry = {
            'rank': fallback_rank,
            'user_id': current_user.id,
            'username': (current_user.username or '').strip() or 'Belum ada',
            'name': (current_user.name or '').strip() or (current_user.username or '').strip() or 'Belum ada',
            'total_score': 0,
            'games_completed': 0,
            'certificate': get_certificate_name(fallback_rank),
            'first_completed_at': None
        }

    return render_template(
        'leaderboard.html',
        leaderboard_top5=leaderboard_top5,
        current_user_entry=current_user_entry
    )

# Dashboard - arahkan ke menu untuk murid
@main.route('/dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == 'guru':
        return redirect(url_for('main.guru_dashboard'))
    elif current_user.role == 'orangtua':
        return redirect(url_for('main.orangtua_dashboard'))
    else:
        return redirect(url_for('main.menu'))

    leaderboard_entries = build_leaderboard_entries()
    leaderboard_top5 = build_top_five_slots(leaderboard_entries)

    current_user_entry = next(
        (entry for entry in leaderboard_entries if entry['user_id'] == current_user.id),
        None
    )

    if current_user_entry is None:
        fallback_rank = len(leaderboard_entries) + 1
        current_user_entry = {
            'rank': fallback_rank,
            'user_id': current_user.id,
            'username': (current_user.username or '').strip() or 'Belum ada',
            'name': (current_user.name or '').strip() or (current_user.username or '').strip() or 'Belum ada',
            'total_score': 0,
            'games_completed': 0,
            'certificate': get_certificate_name(fallback_rank),
            'first_completed_at': None
        }

    return render_template(
        'leaderboard.html',
        leaderboard_top5=leaderboard_top5,
        current_user_entry=current_user_entry
    )

@main.route('/api/leaderboard')
@login_required
def api_leaderboard():
    """Return leaderboard data for AJAX refresh."""
    entries = build_leaderboard_entries()
    top_five = build_top_five_slots(entries)
    current_entry = next((entry for entry in entries if entry['user_id'] == current_user.id), None)

    if current_entry is None:
        current_entry = {
            'rank': len(entries) + 1,
            'username': (current_user.username or '').strip() or 'Belum ada',
            'name': (current_user.name or '').strip() or (current_user.username or '').strip() or 'Belum ada',
            'total_score': 0,
            'games_completed': 0,
            'certificate': get_certificate_name(len(entries) + 1)
        }

    return jsonify({
        'leaders': [
            {
                'rank': leader['rank'],
                'username': leader['username'],
                'name': leader['name'],
                'total_score': leader['total_score'],
                'games_completed': leader['games_completed'],
                'certificate': leader['certificate']
            } for leader in top_five
        ],
        'current': {
            'rank': current_entry['rank'],
            'username': current_entry['username'],
            'name': current_entry['name'],
            'total_score': current_entry['total_score'],
            'games_completed': current_entry['games_completed'],
            'certificate': current_entry['certificate']
        }
    })

@main.route('/badges')
@login_required
def badges():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))

    earned_badge_ids = [ub.badge_id for ub in UserBadge.query.filter_by(user_id=current_user.id).all()]
    badges = Badge.query.order_by(Badge.level_minimum).all()
    return render_template('badges.html', badges=badges, earned_badge_ids=earned_badge_ids)

@main.route('/features')
def features():
    return render_template('features.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/mascot')
def mascot():
    return render_template('mascot.html')

# Guru Dashboard
@main.route('/guru-dashboard')
@login_required
def guru_dashboard():
    if current_user.role not in ['guru', 'admin']:
        flash('Access denied! Hanya Guru yang bisa mengakses halaman ini.', 'danger')
        return redirect(url_for('main.index'))

    # All students
    students = User.query.filter(func.lower(User.role).in_(STUDENT_ROLES)).order_by(User.name).all()
    # All parents
    parents = User.query.filter(func.lower(User.role).in_(['orangtua', 'orang_tua'])).order_by(User.name).all()
    teacher_accounts = (
        User.query
        .filter(func.lower(User.role).in_(['guru', 'admin']))
        .order_by(User.created_at.desc(), User.name.asc())
        .all()
    )

    account_rows = (
        User.query
        .filter(func.lower(User.role).in_(ACCOUNT_MANAGEMENT_ROLES))
        .order_by(User.username.asc())
        .all()
    )
    account_management_users = [
        {
            'id': account.id,
            'username': (account.username or '').strip() or '-',
            'role': normalize_account_role(account.role),
            'role_display': get_role_display_name(account.role),
            'created_at': account.created_at,
        }
        for account in account_rows
    ]

    parent_lookup = {parent.id: parent for parent in parents}
    student_lookup = {student.id: student for student in students}

    assignment_links = ParentStudent.query.order_by(ParentStudent.created_at.desc()).all()
    parent_student_assignments = []
    for link in assignment_links:
        parent_obj = parent_lookup.get(link.parent_id)
        student_obj = student_lookup.get(link.student_id)
        if not parent_obj or not student_obj:
            continue
        parent_student_assignments.append({
            'id': link.id,
            'parent_id': parent_obj.id,
            'parent_name': (parent_obj.name or parent_obj.username or '').strip() or 'Belum ada',
            'parent_username': (parent_obj.username or '').strip() or '-',
            'student_id': student_obj.id,
            'student_name': (student_obj.name or student_obj.username or '').strip() or 'Belum ada',
            'student_username': (student_obj.username or '').strip() or '-',
            'created_at': link.created_at,
        })

    teacher_ids = {current_user.id}
    teacher_ids.update(note.teacher_id for note in TeacherNote.query.with_entities(TeacherNote.teacher_id).all())
    teacher_lookup = {
        teacher.id: teacher
        for teacher in User.query.filter(User.id.in_(teacher_ids)).all()
    }

    teacher_notes_rows = TeacherNote.query.order_by(TeacherNote.created_at.desc()).limit(30).all()
    teacher_notes = []
    for note in teacher_notes_rows:
        student_obj = student_lookup.get(note.student_id)
        if not student_obj:
            continue
        teacher_obj = teacher_lookup.get(note.teacher_id)
        teacher_notes.append({
            'id': note.id,
            'teacher_name': (teacher_obj.name if teacher_obj else None) or 'Guru',
            'student_name': (student_obj.name or student_obj.username or '').strip() or 'Belum ada',
            'student_username': (student_obj.username or '').strip() or '-',
            'note': note.note,
            'created_at': note.created_at,
        })

    # Leaderboard entries (all students ranked by score)
    leaderboard = build_leaderboard_entries()

    # Per-student game play data
    game_plays = GamePlay.query.all()
    plays_by_user = {}
    for gp in game_plays:
        plays_by_user.setdefault(gp.user_id, []).append(gp)

    student_data = []
    total_scores = []
    for student in students:
        plays = plays_by_user.get(student.id, [])
        total_score = sum(p.score for p in plays)
        games_played = len(plays)
        game_scores = {p.game_name: p.score for p in plays}
        progress_pct = round(games_played / len(GAME_KEYS) * 100) if GAME_KEYS else 0
        student_data.append({
            'id': student.id,
            'name': student.name,
            'username': student.username,
            'kelas': student.kelas or '-',
            'total_score': total_score,
            'games_played': games_played,
            'progress_pct': progress_pct,
            'game_scores': game_scores,
        })
        total_scores.append(total_score)

    avg_score = round(sum(total_scores) / len(total_scores), 1) if total_scores else 0
    active_students = sum(1 for s in student_data if s['games_played'] > 0)
    total_plays = sum(s['games_played'] for s in student_data)

    stats = {
        'total_students': len(students),
        'total_parents': len(parents),
        'avg_score': avg_score,
        'active_students': active_students,
        'total_plays': total_plays,
    }

    access_setting = get_access_time_setting(create_if_missing=True)
    access_time = {
        'start_time': format_hhmm(access_setting.start_time) if access_setting else format_hhmm(DEFAULT_ACCESS_START),
        'end_time': format_hhmm(access_setting.end_time) if access_setting else format_hhmm(DEFAULT_ACCESS_END),
    }

    mission_access_setting = get_daily_mission_access_time_setting(create_if_missing=True)
    mission_access_time = {
        'start_time': format_hhmm(mission_access_setting.start_time) if mission_access_setting else format_hhmm(DEFAULT_DAILY_MISSION_ACCESS_START),
        'end_time': format_hhmm(mission_access_setting.end_time) if mission_access_setting else format_hhmm(DEFAULT_DAILY_MISSION_ACCESS_END),
    }

    menu_access_setting = get_student_menu_access_time_setting(create_if_missing=True)
    student_menu_access_time = {
        'start_time': format_hhmm(menu_access_setting.start_time) if menu_access_setting else format_hhmm(DEFAULT_MENU_ACCESS_START),
        'end_time': format_hhmm(menu_access_setting.end_time) if menu_access_setting else format_hhmm(DEFAULT_MENU_ACCESS_END),
    }

    all_materi = Materi.query.order_by(Materi.created_at.desc()).all()
    question_bank_rows = Soal.query.order_by(Soal.created_at.desc(), Soal.id.desc()).all()
    today = date.today()

    adventure_rules_by_game = {
        'huruf': HURUF_LEVEL_RULES,
        'angka': ANGKA_LEVEL_RULES,
        'warna': WARNA_BENTUK_LEVEL_RULES,
    }

    adventure_slots = []
    for game_key, rules in adventure_rules_by_game.items():
        slots = ensure_adventure_question_map(game_key, rules)
        question_by_id = _get_soal_by_ids([s.question_id for s in slots if s.question_id])
        for slot in sorted(slots, key=lambda s: (s.level, s.question_order)):
            row = question_by_id.get(slot.question_id)
            adventure_slots.append({
                'game_key': game_key,
                'level': slot.level,
                'question_order': slot.question_order,
                'question_id': slot.question_id,
                'question_label': (row.pertanyaan[:55] + '...') if row and row.pertanyaan and len(row.pertanyaan) > 55 else (row.pertanyaan if row else '-'),
            })

    daily_rows = get_or_generate_daily_mission_rows(today)
    daily_question_by_id = _get_soal_by_ids([r.question_id for r in daily_rows if r.question_id])
    daily_mission_slots = []
    for row in daily_rows:
        q = daily_question_by_id.get(row.question_id)
        daily_mission_slots.append({
            'question_order': row.question_order,
            'question_id': row.question_id,
            'question_label': (q.pertanyaan[:55] + '...') if q and q.pertanyaan and len(q.pertanyaan) > 55 else (q.pertanyaan if q else '-'),
            'set_by_teacher': bool(row.set_by_teacher),
        })

    question_usage_daily = {
        row.question_id
        for row in QuestionUsage.query.filter_by(context='daily_mission', is_active=True).all()
    }
    question_usage_adventure = {
        row.question_id
        for row in QuestionUsage.query.filter_by(context='adventure_map', is_active=True).all()
    }

    usage_updated = False
    for row in question_bank_rows:
        # Semua soal dianggap aktif untuk dua konteks: misi harian dan peta petualangan.
        needs_refresh_usage = (
            (row.id not in question_usage_daily)
            or (row.id not in question_usage_adventure)
            or (not bool(row.use_in_daily_mission))
            or (not bool(row.use_in_adventure_map))
        )
        if needs_refresh_usage:
            row.use_in_daily_mission = True
            row.use_in_adventure_map = True
            _set_question_usages(
                question_id=row.id,
                include_daily_mission=True,
                include_adventure_map=True,
                category=row.kategori,
            )
            usage_updated = True

        row.is_for_daily_mission = True
        row.is_for_adventure_map = True

    if usage_updated:
        db.session.commit()

    # Semua soal ditampilkan sebagai soal aktif (tanpa konsep soal tidak aktif).
    adventure_active_qids = {slot.get('question_id') for slot in adventure_slots if slot.get('question_id')}
    mission_active_qids = {slot.get('question_id') for slot in daily_mission_slots if slot.get('question_id')}

    soal_aktif = []
    for q in question_bank_rows:
        answer_letter = Soal.answer_key_to_letter(q.jawaban_benar)
        option_map = {
            'A': (q.pilihan_a or '').strip(),
            'B': (q.pilihan_b or '').strip(),
            'C': (q.pilihan_c or '').strip(),
            'D': (q.pilihan_d or '').strip(),
        }
        pemakaian_parts = []
        if q.id in adventure_active_qids:
            pemakaian_parts.append('Peta Petualangan')
        if q.id in mission_active_qids:
            pemakaian_parts.append('Misi Harian')
        if not pemakaian_parts:
            pemakaian_parts.append('Tersedia')
        soal_aktif.append({
            'id': q.id,
            'kategori': q.kategori,
            'pertanyaan': q.pertanyaan or '',
            'answer_letter': answer_letter,
            'answer_label': option_map.get(answer_letter, ''),
            'option_a': option_map['A'],
            'option_b': option_map['B'],
            'option_c': option_map['C'],
            'question_image': _build_static_image_url(q.image_question),
            'option_image_a': _build_static_image_url(q.image_option_a),
            'option_image_b': _build_static_image_url(q.image_option_b),
            'option_image_c': _build_static_image_url(q.image_option_c),
            'pemakaian': ' & '.join(pemakaian_parts),
        })

    return render_template(
        'guru_dashboard.html',
        students=student_data,
        parents=parents,
        teacher_accounts=teacher_accounts,
        raw_students=students,
        leaderboard=leaderboard,
        stats=stats,
        game_keys=GAME_KEYS,
        access_time=access_time,
        mission_access_time=mission_access_time,
        student_menu_access_time=student_menu_access_time,
        parent_student_assignments=parent_student_assignments,
        teacher_notes=teacher_notes,
        account_management_users=account_management_users,
        all_materi=all_materi,
        question_bank_rows=question_bank_rows,
        question_categories=QUESTION_CATEGORIES,
        adventure_slots=adventure_slots,
        daily_mission_slots=daily_mission_slots,
        soal_aktif=soal_aktif,
        today_date=today,
    )


@main.route('/guru-dashboard/tambah-guru', methods=['POST'])
@login_required
def guru_tambah_guru():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not name or not username or not password:
        flash('Nama guru, email/username, dan password wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" sudah digunakan.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    teacher = User(username=username, name=name, role='guru')
    teacher.set_password(password)
    db.session.add(teacher)
    db.session.commit()

    flash(f'Akun guru "{name}" berhasil ditambahkan.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/pengaturan-akses-game', methods=['POST'])
@login_required
def guru_set_game_access_settings():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    section = request.form.get('section', 'peta')

    if section == 'menu':
        menu_start_raw = request.form.get('menu_start_time', '').strip()
        menu_end_raw = request.form.get('menu_end_time', '').strip()

        if not menu_start_raw or not menu_end_raw:
            flash('Semua field jam akses menu wajib diisi.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        try:
            menu_start_time = datetime.strptime(menu_start_raw, '%H:%M').time()
            menu_end_time = datetime.strptime(menu_end_raw, '%H:%M').time()
        except ValueError:
            flash('Format jam akses menu tidak valid. Gunakan format HH:MM.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        if menu_start_time >= menu_end_time:
            flash('Jam mulai akses menu harus lebih kecil dari jam selesai.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        menu_setting = get_student_menu_access_time_setting(create_if_missing=True)
        menu_setting.start_time = menu_start_time
        menu_setting.end_time = menu_end_time
        db.session.commit()

        flash(
            'Pengaturan akses menu murid berhasil disimpan. '
            f'Menu: {format_hhmm(menu_start_time)} - {format_hhmm(menu_end_time)}.',
            'success'
        )
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    if section == 'peta':
        peta_start_raw = request.form.get('peta_start_time', '').strip()
        peta_end_raw = request.form.get('peta_end_time', '').strip()

        if not peta_start_raw or not peta_end_raw:
            flash('Jam mulai dan jam selesai Peta Petualangan wajib diisi.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        try:
            peta_start_time = datetime.strptime(peta_start_raw, '%H:%M').time()
            peta_end_time = datetime.strptime(peta_end_raw, '%H:%M').time()
        except ValueError:
            flash('Format jam Peta Petualangan tidak valid. Gunakan format HH:MM.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        if peta_start_time >= peta_end_time:
            flash('Jam mulai Peta Petualangan harus lebih kecil dari jam selesai.', 'danger')
            return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

        peta_setting = get_access_time_setting(create_if_missing=True)
        peta_setting.start_time = peta_start_time
        peta_setting.end_time = peta_end_time
        db.session.commit()

        flash(
            'Pengaturan akses Peta Petualangan berhasil disimpan. '
            f'Peta: {format_hhmm(peta_start_time)} - {format_hhmm(peta_end_time)}.',
            'success'
        )
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    flash('Bagian pengaturan tidak dikenali.', 'danger')
    return redirect(url_for('main.guru_dashboard') + '#tab-game-access')


@main.route('/guru-dashboard/pengaturan-jam-akses', methods=['POST'])
@login_required
def guru_set_access_time():
    if request.form.get('peta_start_time') or request.form.get('mission_start_time'):
        return guru_set_game_access_settings()

    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    start_raw = request.form.get('start_time', '').strip()
    end_raw = request.form.get('end_time', '').strip()

    if not start_raw or not end_raw:
        flash('Jam mulai dan jam selesai Peta Petualangan wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    try:
        start_time = datetime.strptime(start_raw, '%H:%M').time()
        end_time = datetime.strptime(end_raw, '%H:%M').time()
    except ValueError:
        flash('Format jam Peta Petualangan tidak valid. Gunakan format HH:MM.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    if start_time >= end_time:
        flash('Jam mulai Peta Petualangan harus lebih kecil dari jam selesai.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    setting = get_access_time_setting(create_if_missing=True)
    setting.start_time = start_time
    setting.end_time = end_time
    db.session.commit()

    flash(f'Jam akses Peta Petualangan berhasil diperbarui: {format_hhmm(start_time)} - {format_hhmm(end_time)}.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-game-access')


@main.route('/guru-dashboard/pengaturan-jam-akses-misi-harian', methods=['POST'])
@login_required
def guru_set_daily_mission_access_time():
    if request.form.get('peta_start_time') or request.form.get('mission_start_time') and request.form.get('peta_end_time'):
        return guru_set_game_access_settings()

    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    start_raw = request.form.get('mission_start_time', '').strip()
    end_raw = request.form.get('mission_end_time', '').strip()

    if not start_raw or not end_raw:
        flash('Jam mulai dan jam selesai Misi Harian wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    try:
        start_time = datetime.strptime(start_raw, '%H:%M').time()
        end_time = datetime.strptime(end_raw, '%H:%M').time()
    except ValueError:
        flash('Format jam Misi Harian tidak valid. Gunakan format HH:MM.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    if start_time >= end_time:
        flash('Jam mulai Misi Harian harus lebih kecil dari jam selesai.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-game-access')

    setting = get_daily_mission_access_time_setting(create_if_missing=True)
    setting.start_time = start_time
    setting.end_time = end_time
    db.session.commit()

    flash(f'Jam akses Misi Harian berhasil diperbarui: {format_hhmm(start_time)} - {format_hhmm(end_time)}.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-game-access')


@main.route('/guru-dashboard/bank-soal/tambah', methods=['POST'])
@login_required
def guru_tambah_bank_soal():
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    kategori = normalize_question_category(request.form.get('kategori', ''))
    pertanyaan = request.form.get('pertanyaan', '').strip() or 'Pilih jawaban yang benar berdasarkan gambar.'
    pilihan_a = request.form.get('pilihan_a', '').strip() or 'Opsi A'
    pilihan_b = request.form.get('pilihan_b', '').strip() or 'Opsi B'
    pilihan_c = request.form.get('pilihan_c', '').strip() or 'Opsi C'
    jawaban_benar = Soal.answer_key_to_letter(request.form.get('jawaban_benar', 'A'))

    include_daily_mission = True
    include_adventure_map = True

    if not kategori:
        flash('Kategori soal tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    if jawaban_benar not in ['A', 'B', 'C']:
        flash('Jawaban benar harus salah satu dari A/B/C.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    question_image_file = request.files.get('image_question_file')
    option_a_image_file = request.files.get('image_option_a_file')
    option_b_image_file = request.files.get('image_option_b_file')
    option_c_image_file = request.files.get('image_option_c_file')

    required_files = [question_image_file, option_a_image_file, option_b_image_file, option_c_image_file]
    if any((file_obj is None or not (file_obj.filename or '').strip()) for file_obj in required_files):
        flash('Upload gambar soal dan semua gambar opsi (A, B, C) wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    try:
        question_image = _save_question_image(question_image_file, 'question')
        option_a_image = _save_question_image(option_a_image_file, 'option_a')
        option_b_image = _save_question_image(option_b_image_file, 'option_b')
        option_c_image = _save_question_image(option_c_image_file, 'option_c')
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    row = Soal(
        kategori=kategori,
        pertanyaan=pertanyaan,
        pilihan_a=pilihan_a,
        pilihan_b=pilihan_b,
        pilihan_c=pilihan_c,
        pilihan_d=None,
        jawaban_benar=jawaban_benar,
        question_type='image_mcq',
        image_question=question_image,
        image_option_a=option_a_image,
        image_option_b=option_b_image,
        image_option_c=option_c_image,
        image_option_d=None,
        use_in_daily_mission=include_daily_mission,
        use_in_adventure_map=include_adventure_map,
        difficulty='mudah',
    )
    db.session.add(row)
    db.session.flush()

    _set_question_usages(
        question_id=row.id,
        include_daily_mission=include_daily_mission,
        include_adventure_map=include_adventure_map,
        category=row.kategori,
    )

    assign_to = (request.form.get('assign_to') or '').strip()
    if assign_to == 'peta':
        game_key = (request.form.get('peta_game_key') or '').strip()
        try:
            level = int(request.form.get('peta_level', '1'))
            question_order = int(request.form.get('peta_question_order', '1'))
        except (TypeError, ValueError):
            level, question_order = 1, 1

        if game_key in ('huruf', 'angka', 'warna'):
            slot = AdventureQuestionMap.query.filter_by(
                game_key=game_key,
                level=level,
                question_order=question_order
            ).first()
            if slot:
                slot.question_id = row.id
            else:
                db.session.add(AdventureQuestionMap(
                    game_key=game_key,
                    level=level,
                    question_order=question_order,
                    question_id=row.id,
                ))
    elif assign_to == 'misi':
        try:
            question_order = int(request.form.get('misi_question_order', '1'))
        except (TypeError, ValueError):
            question_order = 1

        today = date.today()
        slot = DailyMissionQuestion.query.filter_by(
            tanggal=today,
            question_order=question_order
        ).first()
        if slot:
            slot.question_id = row.id
            slot.set_by_teacher = True
        else:
            db.session.add(DailyMissionQuestion(
                tanggal=today,
                question_order=question_order,
                question_id=row.id,
                set_by_teacher=True,
            ))

    db.session.commit()

    flash('Soal baru berhasil ditambahkan ke Kelola Soal.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')


@main.route('/guru-dashboard/bank-soal/edit/<int:question_id>', methods=['POST'])
@login_required
def guru_edit_bank_soal(question_id):
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    source_tab = request.form.get('source_tab', 'kelola-soal')
    redirect_tab = source_tab if source_tab in ('kelola-soal', 'bank-soal', 'soal-aktif') else 'kelola-soal'
    row = Soal.query.get_or_404(question_id)

    kategori = normalize_question_category(request.form.get('kategori', row.kategori))
    pertanyaan = request.form.get('pertanyaan', row.pertanyaan).strip() or row.pertanyaan
    pilihan_a = request.form.get('pilihan_a', row.pilihan_a).strip() or row.pilihan_a
    pilihan_b = request.form.get('pilihan_b', row.pilihan_b).strip() or row.pilihan_b
    pilihan_c = request.form.get('pilihan_c', row.pilihan_c).strip() or row.pilihan_c
    jawaban_benar = Soal.answer_key_to_letter(request.form.get('jawaban_benar', row.jawaban_benar))

    include_daily_mission = True
    include_adventure_map = True

    if not kategori:
        flash('Kategori soal tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)

    if jawaban_benar not in ['A', 'B', 'C']:
        flash('Jawaban benar harus salah satu dari A/B/C.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)

    if not (pilihan_a and pilihan_b and pilihan_c):
        flash('Label opsi A, B, dan C tidak boleh kosong saat edit.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)

    try:
        question_image_file = request.files.get('image_question_file')
        option_a_image_file = request.files.get('image_option_a_file')
        option_b_image_file = request.files.get('image_option_b_file')
        option_c_image_file = request.files.get('image_option_c_file')

        if question_image_file and (question_image_file.filename or '').strip():
            new_path = _save_question_image(question_image_file, 'question')
            _delete_question_image(row.image_question)
            row.image_question = new_path

        if option_a_image_file and (option_a_image_file.filename or '').strip():
            new_path = _save_question_image(option_a_image_file, 'option_a')
            _delete_question_image(row.image_option_a)
            row.image_option_a = new_path

        if option_b_image_file and (option_b_image_file.filename or '').strip():
            new_path = _save_question_image(option_b_image_file, 'option_b')
            _delete_question_image(row.image_option_b)
            row.image_option_b = new_path

        if option_c_image_file and (option_c_image_file.filename or '').strip():
            new_path = _save_question_image(option_c_image_file, 'option_c')
            _delete_question_image(row.image_option_c)
            row.image_option_c = new_path
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)

    row.kategori = kategori
    row.pertanyaan = pertanyaan
    row.pilihan_a = pilihan_a
    row.pilihan_b = pilihan_b
    row.pilihan_c = pilihan_c
    row.pilihan_d = None
    row.jawaban_benar = jawaban_benar
    row.question_type = 'image_mcq'
    row.use_in_daily_mission = True
    row.use_in_adventure_map = True

    required_images = [
        row.image_question,
        row.image_option_a,
        row.image_option_b,
        row.image_option_c,
    ]
    if any(not (img or '').strip() for img in required_images):
        flash('Gambar soal dan gambar opsi A/B/C wajib tersedia setelah edit.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)

    _set_question_usages(
        question_id=row.id,
        include_daily_mission=include_daily_mission,
        include_adventure_map=include_adventure_map,
        category=row.kategori,
    )
    db.session.commit()

    flash('Soal berhasil diperbarui.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)


@main.route('/guru-dashboard/bank-soal/hapus/<int:question_id>', methods=['POST'])
@login_required
def guru_hapus_bank_soal(question_id):
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    source_tab = request.form.get('source_tab', 'kelola-soal')
    redirect_tab = source_tab if source_tab in ('kelola-soal', 'bank-soal', 'soal-aktif') else 'kelola-soal'
    row = Soal.query.get_or_404(question_id)
    _delete_question_image(row.image_question)
    _delete_question_image(row.image_option_a)
    _delete_question_image(row.image_option_b)
    _delete_question_image(row.image_option_c)
    _delete_question_image(row.image_option_d)

    QuestionUsage.query.filter_by(question_id=row.id).delete()
    AdventureQuestionMap.query.filter_by(question_id=row.id).update({'question_id': None})
    DailyMissionQuestion.query.filter_by(question_id=row.id).update({'question_id': None})
    db.session.delete(row)
    db.session.commit()

    flash('Soal berhasil dihapus dari Kelola Soal.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-' + redirect_tab)


@main.route('/guru-dashboard/soal-aktif/tambah', methods=['POST'])
@login_required
def guru_tambah_soal_aktif():
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    kategori = normalize_question_category(request.form.get('kategori', ''))
    pertanyaan = request.form.get('pertanyaan', '').strip() or 'Pilih jawaban yang benar berdasarkan gambar.'
    pilihan_a = request.form.get('pilihan_a', '').strip() or 'Opsi A'
    pilihan_b = request.form.get('pilihan_b', '').strip() or 'Opsi B'
    pilihan_c = request.form.get('pilihan_c', '').strip() or 'Opsi C'
    jawaban_benar = Soal.answer_key_to_letter(request.form.get('jawaban_benar', 'A'))

    if not kategori:
        flash('Kategori soal tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    if jawaban_benar not in ['A', 'B', 'C']:
        flash('Jawaban benar harus salah satu dari A/B/C.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    question_image_file = request.files.get('image_question_file')
    option_a_image_file = request.files.get('image_option_a_file')
    option_b_image_file = request.files.get('image_option_b_file')
    option_c_image_file = request.files.get('image_option_c_file')

    required_files = [question_image_file, option_a_image_file, option_b_image_file, option_c_image_file]
    if any((f is None or not (f.filename or '').strip()) for f in required_files):
        flash('Upload gambar soal dan semua gambar opsi (A, B, C) wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    try:
        question_image = _save_question_image(question_image_file, 'question')
        option_a_image = _save_question_image(option_a_image_file, 'option_a')
        option_b_image = _save_question_image(option_b_image_file, 'option_b')
        option_c_image = _save_question_image(option_c_image_file, 'option_c')
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    soal = Soal(
        kategori=kategori,
        pertanyaan=pertanyaan,
        pilihan_a=pilihan_a,
        pilihan_b=pilihan_b,
        pilihan_c=pilihan_c,
        pilihan_d=None,
        jawaban_benar=jawaban_benar,
        question_type='image_mcq',
        image_question=question_image,
        image_option_a=option_a_image,
        image_option_b=option_b_image,
        image_option_c=option_c_image,
        image_option_d=None,
        use_in_daily_mission=True,
        use_in_adventure_map=True,
        difficulty='mudah',
    )
    db.session.add(soal)
    db.session.flush()

    _set_question_usages(
        question_id=soal.id,
        include_daily_mission=True,
        include_adventure_map=True,
        category=soal.kategori,
    )

    assign_to = (request.form.get('assign_to') or '').strip()
    if assign_to == 'peta':
        game_key = (request.form.get('peta_game_key') or '').strip()
        try:
            level = int(request.form.get('peta_level', '1'))
            question_order = int(request.form.get('peta_question_order', '1'))
        except (TypeError, ValueError):
            level, question_order = 1, 1
        if game_key in ('huruf', 'angka', 'warna'):
            slot = AdventureQuestionMap.query.filter_by(
                game_key=game_key,
                level=level,
                question_order=question_order
            ).first()
            if slot:
                slot.question_id = soal.id
            else:
                db.session.add(AdventureQuestionMap(
                    game_key=game_key,
                    level=level,
                    question_order=question_order,
                    question_id=soal.id,
                ))
    elif assign_to == 'misi':
        try:
            question_order = int(request.form.get('misi_question_order', '1'))
        except (TypeError, ValueError):
            question_order = 1
        today = date.today()
        slot = DailyMissionQuestion.query.filter_by(
            tanggal=today,
            question_order=question_order
        ).first()
        if slot:
            slot.question_id = soal.id
            slot.set_by_teacher = True
        else:
            db.session.add(DailyMissionQuestion(
                tanggal=today,
                question_order=question_order,
                question_id=soal.id,
                set_by_teacher=True,
            ))

    db.session.commit()
    flash('Soal baru berhasil ditambahkan dan ditetapkan sebagai Soal Aktif.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')


@main.route('/guru-dashboard/peta-soal/ganti', methods=['POST'])
@login_required
def guru_ganti_soal_peta():
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    game_key = (request.form.get('game_key') or '').strip()
    try:
        level = int(request.form.get('level', '0'))
        question_order = int(request.form.get('question_order', '0'))
        question_id = int(request.form.get('question_id', '0'))
    except ValueError:
        flash('Data slot soal tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    if game_key not in ['huruf', 'angka', 'warna']:
        flash('Game peta tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    target_question = Soal.query.get(question_id)
    if not target_question:
        flash('Soal baru tidak ditemukan.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    target_game = get_adventure_game_key_for_category(target_question.kategori)
    if target_game != game_key:
        flash('Kategori soal tidak cocok untuk map/game yang dipilih.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    slot = AdventureQuestionMap.query.filter_by(game_key=game_key, level=level, question_order=question_order).first()
    if not slot:
        slot = AdventureQuestionMap(game_key=game_key, level=level, question_order=question_order, question_id=question_id)
        db.session.add(slot)
    else:
        slot.question_id = question_id
    db.session.commit()

    flash('Soal Peta Petualangan berhasil diganti.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')


@main.route('/guru-dashboard/misi-harian-soal/ganti', methods=['POST'])
@login_required
def guru_ganti_soal_misi_harian():
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    try:
        question_order = int(request.form.get('question_order', '0'))
        question_id = int(request.form.get('question_id', '0'))
    except ValueError:
        flash('Data slot misi harian tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    target_question = Soal.query.get(question_id)
    if not target_question:
        flash('Soal baru tidak ditemukan.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    if not normalize_mission_category(target_question.kategori):
        flash('Soal tidak valid untuk Misi Harian.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')

    today = date.today()
    row = DailyMissionQuestion.query.filter_by(tanggal=today, question_order=question_order).first()
    if not row:
        row = DailyMissionQuestion(
            tanggal=today,
            question_order=question_order,
            question_id=question_id,
            set_by_teacher=True,
        )
        db.session.add(row)
    else:
        row.question_id = question_id
        row.set_by_teacher = True

    db.session.commit()

    flash('Soal Misi Harian hari ini berhasil diganti.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')


# --- Guru: Add student ---
@main.route('/guru-dashboard/tambah-murid', methods=['POST'])
@login_required
def guru_tambah_murid():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    kelas = request.form.get('kelas', '').strip()

    if not name or not username or not password:
        flash('Nama, username, dan password wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" sudah digunakan.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    user = User(username=username, name=name, role='murid', kelas=kelas)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'Murid "{name}" berhasil ditambahkan.', 'success')
    return redirect(url_for('main.guru_dashboard'))


# --- Guru: Edit student ---
@main.route('/guru-dashboard/edit-murid/<int:user_id>', methods=['POST'])
@login_required
def guru_edit_murid(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    student = User.query.get_or_404(user_id)
    if (student.role or '').lower() not in STUDENT_ROLES:
        flash('User ini bukan murid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    kelas = request.form.get('kelas', '').strip()
    password = request.form.get('password', '').strip()

    if not name or not username:
        flash('Nama dan username wajib diisi saat edit murid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    existing = User.query.filter(User.username == username, User.id != user_id).first()
    if existing:
        flash(f'Username "{username}" sudah digunakan akun lain.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    student.name = name
    student.username = username
    student.kelas = kelas

    # Only update password when guru/admin provides a new one.
    if password:
        student.set_password(password)

    db.session.commit()
    flash(f'Data murid "{student.name}" berhasil diperbarui.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/reset-password/<int:user_id>', methods=['POST'])
@login_required
def guru_reset_user_password(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    target_user = User.query.get_or_404(user_id)
    target_role = normalize_account_role(target_user.role)
    if target_role not in ['murid', 'orang_tua']:
        flash('Reset password hanya untuk akun murid atau orang tua.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    new_password = generate_reset_password(8)
    target_user.set_password(new_password)

    db.session.add(PasswordResetLog(
        teacher_id=current_user.id,
        user_id=target_user.id,
        reset_time=datetime.utcnow(),
    ))
    db.session.commit()

    flash(
        f'Password baru untuk {target_user.username} ({get_role_display_name(target_user.role)}) adalah: {new_password}. '
        f'Simpan sekarang karena hanya ditampilkan sekali.',
        'success'
    )
    return redirect(url_for('main.guru_dashboard'))


# --- Guru: Delete student ---
@main.route('/guru-dashboard/hapus-murid/<int:user_id>', methods=['POST'])
@login_required
def guru_hapus_murid(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    user = User.query.get_or_404(user_id)
    if func.lower(user.role) not in STUDENT_ROLES and user.role.lower() not in STUDENT_ROLES:
        flash('User ini bukan murid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    # Delete related records first to avoid FK violations
    GamePlay.query.filter_by(user_id=user_id).delete()
    GameSession.query.filter_by(user_id=user_id).delete()
    UserProgress.query.filter_by(user_id=user_id).delete()
    UserGameHistory.query.filter_by(user_id=user_id).delete()
    UserScore.query.filter_by(user_id=user_id).delete()
    UserBadge.query.filter_by(user_id=user_id).delete()
    ParentStudent.query.filter_by(student_id=user_id).delete()
    TeacherNote.query.filter_by(student_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Murid "{user.name}" berhasil dihapus.', 'success')
    return redirect(url_for('main.guru_dashboard'))


# --- Guru: Add parent ---
@main.route('/guru-dashboard/tambah-orangtua', methods=['POST'])
@login_required
def guru_tambah_orangtua():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not name or not username or not password:
        flash('Nama, username, dan password wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" sudah digunakan.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    user = User(username=username, name=name, role='orangtua')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'Orang Tua "{name}" berhasil ditambahkan.', 'success')
    return redirect(url_for('main.guru_dashboard'))


# --- Guru: Delete parent ---
@main.route('/guru-dashboard/hapus-orangtua/<int:user_id>', methods=['POST'])
@login_required
def guru_hapus_orangtua(user_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    user = User.query.get_or_404(user_id)
    if normalize_account_role(user.role) != 'orang_tua':
        flash('User ini bukan orang tua.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    ParentStudent.query.filter_by(parent_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Orang Tua "{user.name}" berhasil dihapus.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/relasi-orangtua-anak', methods=['POST'])
@login_required
def guru_set_parent_student_relation():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    try:
        parent_id = int(request.form.get('parent_id', '0'))
        student_id = int(request.form.get('student_id', '0'))
    except ValueError:
        flash('Data orang tua / murid tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    parent = User.query.get(parent_id)
    student = User.query.get(student_id)

    if not parent or normalize_account_role(parent.role) != 'orang_tua':
        flash('Orang tua tidak ditemukan atau role tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if not student or (student.role or '').lower() not in STUDENT_ROLES:
        flash('Murid tidak ditemukan atau role tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    exists = ParentStudent.query.filter_by(parent_id=parent_id, student_id=student_id).first()
    if exists:
        flash('Relasi orang tua dan murid ini sudah ada.', 'warning')
        return redirect(url_for('main.guru_dashboard'))

    existing_student_relation = ParentStudent.query.filter_by(student_id=student_id).first()
    if existing_student_relation:
        current_parent = User.query.get(existing_student_relation.parent_id)
        parent_name = (current_parent.name if current_parent else None) or 'orang tua lain'
        flash(f'Murid ini sudah terhubung dengan {parent_name}. Ubah lewat tombol Edit relasi.', 'warning')
        return redirect(url_for('main.guru_dashboard'))

    db.session.add(ParentStudent(parent_id=parent_id, student_id=student_id))
    db.session.commit()
    flash(f'Relasi {parent.name} dengan {student.name} berhasil ditambahkan.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/relasi-orangtua-anak/edit/<int:relation_id>', methods=['POST'])
@login_required
def guru_edit_parent_student_relation(relation_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    relation = ParentStudent.query.get_or_404(relation_id)

    try:
        parent_id = int(request.form.get('parent_id', '0'))
        student_id = int(request.form.get('student_id', '0'))
    except ValueError:
        flash('Data orang tua / murid tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    parent = User.query.get(parent_id)
    student = User.query.get(student_id)

    if not parent or normalize_account_role(parent.role) != 'orang_tua':
        flash('Orang tua tidak ditemukan atau role tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if not student or (student.role or '').lower() not in STUDENT_ROLES:
        flash('Murid tidak ditemukan atau role tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    duplicate_pair = (
        ParentStudent.query
        .filter(
            ParentStudent.parent_id == parent_id,
            ParentStudent.student_id == student_id,
            ParentStudent.id != relation_id,
        )
        .first()
    )
    if duplicate_pair:
        flash('Relasi orang tua dan murid ini sudah ada.', 'warning')
        return redirect(url_for('main.guru_dashboard'))

    existing_student_relation = (
        ParentStudent.query
        .filter(ParentStudent.student_id == student_id, ParentStudent.id != relation_id)
        .first()
    )
    if existing_student_relation:
        current_parent = User.query.get(existing_student_relation.parent_id)
        parent_name = (current_parent.name if current_parent else None) or 'orang tua lain'
        flash(f'Murid ini sudah terhubung dengan {parent_name}.', 'warning')
        return redirect(url_for('main.guru_dashboard'))

    relation.parent_id = parent_id
    relation.student_id = student_id
    db.session.commit()

    flash('Relasi orang tua dan murid berhasil diperbarui.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/relasi-orangtua-anak/hapus/<int:relation_id>', methods=['POST'])
@login_required
def guru_hapus_parent_student_relation(relation_id):
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    relation = ParentStudent.query.get_or_404(relation_id)
    db.session.delete(relation)
    db.session.commit()
    flash('Relasi orang tua dan murid berhasil dihapus.', 'success')
    return redirect(url_for('main.guru_dashboard'))


@main.route('/guru-dashboard/catatan-guru', methods=['POST'])
@login_required
def guru_tambah_catatan():
    if current_user.role not in ['guru', 'admin']:
        return jsonify({'ok': False, 'msg': 'Akses ditolak'}), 403

    note_text = request.form.get('note', '').strip()
    try:
        student_id = int(request.form.get('student_id', '0'))
    except ValueError:
        flash('Pilih murid yang valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    if not note_text:
        flash('Isi catatan tidak boleh kosong.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    student = User.query.get(student_id)
    if not student or (student.role or '').lower() not in STUDENT_ROLES:
        flash('Murid tidak ditemukan atau role tidak valid.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    db.session.add(TeacherNote(
        teacher_id=current_user.id,
        student_id=student_id,
        note=note_text,
        created_at=datetime.utcnow(),
    ))
    db.session.commit()
    flash('Catatan guru berhasil disimpan.', 'success')
    return redirect(url_for('main.guru_dashboard'))


# Orang Tua Dashboard
@main.route('/orangtua-dashboard')
@login_required
def orangtua_dashboard():
    if normalize_account_role(current_user.role) != 'orang_tua':
        flash('Access denied! Hanya Orang Tua yang bisa mengakses dashboard orang tua.', 'danger')
        return redirect(url_for('main.index'))

    child_links = ParentStudent.query.filter_by(parent_id=current_user.id).all()
    child_ids = sorted({link.student_id for link in child_links})

    children = []
    if child_ids:
        children = User.query.filter(User.id.in_(child_ids)).order_by(User.name.asc()).all()
        child_ids = [child.id for child in children if (child.role or '').lower() in STUDENT_ROLES]

    leaderboard = build_leaderboard_entries()
    leaderboard_rank_map = {entry['user_id']: entry['rank'] for entry in leaderboard}
    today = date.today()

    child_profiles = []
    child_daily_progress = []
    if child_ids:
        plays = (
            GamePlay.query
            .filter(GamePlay.user_id.in_(child_ids))
            .order_by(GamePlay.played_at.desc())
            .all()
        )
        progress_rows = UserProgress.query.filter(UserProgress.user_id.in_(child_ids)).all()
        progress_harian_rows = ProgresHarian.query.filter(
            ProgresHarian.user_id.in_(child_ids),
            ProgresHarian.tanggal == today
        ).all()
        daily_mission_rows = DailyMissionRun.query.filter(
            DailyMissionRun.user_id.in_(child_ids),
            DailyMissionRun.tanggal == today
        ).all()

        plays_by_child = {}
        for play in plays:
            plays_by_child.setdefault(play.user_id, []).append(play)

        progress_harian_by_child = {row.user_id: row for row in progress_harian_rows}
        daily_mission_by_child = {row.user_id: row for row in daily_mission_rows}

        progress_done_count = {child_id: 0 for child_id in child_ids}
        for row in progress_rows:
            if row.status == 'selesai':
                progress_done_count[row.user_id] = progress_done_count.get(row.user_id, 0) + 1

        total_adventure_games = max(1, len(ADVENTURE_GAMES))
        for child in children:
            child_plays = plays_by_child.get(child.id, [])
            total_score = int(sum(play.score for play in child_plays))
            games_played = len(child_plays)
            done_count = min(progress_done_count.get(child.id, 0), total_adventure_games)
            progress_pct = round((done_count / total_adventure_games) * 100)
            latest_play = child_plays[0].played_at if child_plays else None
            games_completed_today = GamePlay.query.filter_by(user_id=child.id, played_date=today).count()
            total_stars = get_total_stars(child.id)
            certificates_count = UserCertificate.query.filter_by(user_id=child.id).count()

            materi_categories = [
                ('huruf', 'A. Mengenal Huruf'),
                ('angka', 'B. Mengenal Angka'),
                ('warna', 'C. Mengenal Warna dan Bentuk Bangun Ruang')
            ]
            daily_progress_items = []
            for category_key, category_name in materi_categories:
                history = UserGameHistory.query.filter_by(
                    user_id=child.id,
                    game_id=category_key,
                    tanggal_main=today
                ).first()

                if not history:
                    percentage = 0
                elif history.status == 'selesai':
                    percentage = 100
                elif (history.total_questions or 0) > 0:
                    percentage = int(min(100, (history.answered_questions / history.total_questions) * 100))
                else:
                    percentage = 0

                daily_progress_items.append({
                    'materi_name': category_name,
                    'percentage': min(percentage, 100)
                })

            total_progress_today = round(
                sum(item['percentage'] for item in daily_progress_items) / max(1, len(daily_progress_items))
            )

            progress_harian = progress_harian_by_child.get(child.id)
            mission_run = daily_mission_by_child.get(child.id)
            mission_done = bool(
                (progress_harian and progress_harian.status_selesai) or
                (mission_run and mission_run.status_selesai)
            )
            mission_completed_at = mission_run.completed_at if mission_run else None
            mission_xp = int(progress_harian.xp_earned or 0) if progress_harian else 0
            mission_bonus = int(progress_harian.bonus or 0) if progress_harian else 0
            mission_reward = mission_xp + mission_bonus

            child_profiles.append({
                'id': child.id,
                'name': (child.name or child.username or '').strip() or 'Belum ada',
                'username': (child.username or '').strip() or '-',
                'kelas': (child.kelas or '-').strip() or '-',
                'xp': int(child.xp or 0),
                'level': int(child.level or 0),
                'total_score': total_score,
                'games_played': games_played,
                'progress_done': done_count,
                'progress_total': total_adventure_games,
                'progress_pct': progress_pct,
                'rank': leaderboard_rank_map.get(child.id),
                'last_played_at': latest_play,
            })

            child_daily_progress.append({
                'child_id': child.id,
                'child_name': (child.name or child.username or '').strip() or 'Belum ada',
                'child_username': (child.username or '').strip() or '-',
                'today_date': today,
                'total_stars': total_stars,
                'level': int(child.level or 0),
                'games_completed': int(games_completed_today),
                'certificates_count': int(certificates_count),
                'daily_progress': daily_progress_items,
                'total_progress_today': int(total_progress_today),
                'mission_status': 'Selesai' if mission_done else 'Belum',
                'mission_completed_at': mission_completed_at,
                'mission_reward': int(mission_reward),
                'mission_xp': mission_xp,
                'mission_bonus': mission_bonus,
            })

    notes_data = []
    if child_ids:
        teacher_notes = (
            TeacherNote.query
            .filter(TeacherNote.student_id.in_(child_ids))
            .order_by(TeacherNote.created_at.desc())
            .all()
        )

        teacher_ids = sorted({note.teacher_id for note in teacher_notes})
        teacher_lookup = {}
        if teacher_ids:
            teacher_lookup = {
                teacher.id: teacher
                for teacher in User.query.filter(User.id.in_(teacher_ids)).all()
            }

        child_lookup = {child.id: child for child in children}
        for note in teacher_notes:
            teacher_obj = teacher_lookup.get(note.teacher_id)
            student_obj = child_lookup.get(note.student_id)
            if not student_obj:
                continue
            notes_data.append({
                'teacher_name': (teacher_obj.name if teacher_obj else None) or 'Guru',
                'student_name': (student_obj.name or student_obj.username or '').strip() or 'Belum ada',
                'created_at': note.created_at,
                'note': note.note,
            })

    return render_template(
        'orangtua_dashboard.html',
        leaderboard=leaderboard,
        child_ids=child_ids,
        children=children,
        child_profiles=child_profiles,
        child_daily_progress=child_daily_progress,
        teacher_notes=notes_data,
    )
# Halaman Register
@main.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        flash('Registrasi hanya dapat dilakukan oleh guru/admin.', 'warning')
        return redirect(url_for('main.login'))

    if current_user.role not in ['guru', 'admin']:
        flash('Registrasi hanya dapat dilakukan oleh guru/admin.', 'warning')
        return redirect(url_for('main.index'))

    flash('Pendaftaran akun dilakukan melalui Dashboard Guru/Admin.', 'info')
    return redirect(url_for('main.guru_dashboard'))

# Halaman Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Will redirect to dashboard eventually
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', '').lower().strip()

        # Cek apakah user ada di database
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.role not in ['murid', 'guru', 'orangtua', 'admin', 'user']:
                flash('Role pengguna tidak dikenali di database.', 'danger')
                return redirect(url_for('main.login'))

            if role.lower() not in ['murid', 'guru', 'orangtua', 'admin', 'user']:
                flash('Role yang dipilih tidak valid.', 'danger')
                return redirect(url_for('main.login'))

            # normalisasi role database lama -> murid
            db_role = user.role.lower()
            if db_role == 'user':
                db_role = 'murid'

            if db_role != role.lower():
                flash('Role tidak sesuai dengan data di database.', 'danger')
                return redirect(url_for('main.login'))

            login_user(user)
            first_login_today = grant_daily_login_star(user.id)
            sync_user_level_from_completed_games(user)
            ensure_day6_certificate(user)
            daily_status = sync_user_daily_status(user.id, date.today())
            db.session.commit()
            flash('Login berhasil!', 'success')
            if db_role == 'murid':
                session['play_login_mission_audio'] = bool(not daily_status.mission_completed and not daily_status.reminder_played)
                return redirect(url_for('main.menu'))
            elif db_role == 'guru':
                return redirect(url_for('main.guru_dashboard'))
            elif db_role == 'orangtua':
                return redirect(url_for('main.orangtua_dashboard'))
            elif db_role == 'admin':
                return redirect(url_for('main.admin_dashboard'))

        else:
            flash('Username atau password salah.', 'danger')
    return render_template('login.html')

@main.route('/misi-harian')
@login_required
def misi_harian():
    if current_user.role == 'admin':
        flash('Access denied! Admin tidak bisa mengakses misi harian pengguna.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()
    daily_status = sync_user_daily_status(current_user.id, today)
    mission_access = get_daily_mission_access_status(today)
    misi_done = bool(daily_status.mission_completed)

    print(f"[DEBUG] Tanggal hari ini: {today}")
    print(f"[DEBUG] Status akses misi: {mission_access}")
    print(f"[DEBUG] Status misi selesai: {misi_done}")

    if misi_done:
        print("[DEBUG] Misi sudah selesai hari ini.")
        return render_template(
            'misi_harian.html',
            questions=[],
            misi_done=True,
            should_play_completion_audio=bool(misi_done and not daily_status.completion_audio_played),
            mission_stats=None,
            mission_time_limit=None,
            mission_access=mission_access,
            mission_locked=True,
            today_iso=today.isoformat(),
            mission_date=None,
            currently_xp=current_user.xp,
            currently_level=current_user.level
        )

    questions = get_daily_mission_questions(current_user.id, today)
    print(f"[DEBUG] Jumlah soal yang diambil: {len(questions) if questions else 0}")
    mission_date = today

    if not questions:
        print("[DEBUG] Tidak ada soal untuk hari ini. Mencoba generate soal baru.")
        get_or_generate_daily_mission_rows(today)
        questions = get_daily_mission_questions(current_user.id, today)
        print(f"[DEBUG] Jumlah soal setelah generate: {len(questions) if questions else 0}")

    if not questions:
        yesterday = today - timedelta(days=1)
        yesterday_rows = DailyMissionQuestion.query.filter_by(tanggal=yesterday).order_by(DailyMissionQuestion.question_order.asc()).all()
        if yesterday_rows:
            print(f"[DEBUG] Tidak ada soal hari ini, menampilkan soal Misi Harian kemarin: {yesterday}")
            questions = get_daily_mission_questions(current_user.id, yesterday)
            mission_date = yesterday
            print(f"[DEBUG] Jumlah soal kemarin yang diambil: {len(questions) if questions else 0}")

    if not questions:
        flash('Database soal misi harian belum mencukupi atau semua soal hari ini sudah dikerjakan.', 'danger')
        return redirect(url_for('main.user_dashboard'))

    return render_template(
        'misi_harian.html',
        questions=[
            # Pastikan field gambar dikonversi ke URL/data-uri agar template bisa menampilkannya
            (lambda d: (
                d.update({
                    'question_image': _build_static_image_url(d.get('question_image')) or _build_visual_image_data(d.get('display') or d.get('answer') or d.get('option_a'), d.get('kategori')),
                    'option_image_a': _build_static_image_url(d.get('option_image_a')) or None,
                    'option_image_b': _build_static_image_url(d.get('option_image_b')) or None,
                    'option_image_c': _build_static_image_url(d.get('option_image_c')) or None,
                    'option_image_d': _build_static_image_url(d.get('option_image_d')) or None,
                }) or d
            ))(q.to_dict())
            for q in questions
        ],
        misi_done=bool(misi_done),
        should_play_completion_audio=bool(misi_done and not daily_status.completion_audio_played),
        mission_stats=None,
        mission_time_limit=DAILY_MISSION_TIME_LIMIT_SECONDS,
        mission_access=mission_access,
        mission_locked=False,
        today_iso=today.isoformat(),
        mission_date=mission_date.isoformat(),
        currently_xp=current_user.xp,
        currently_level=current_user.level
    )

@main.route('/misi-harian/submit', methods=['POST'])
@login_required
def misi_harian_submit():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()
    daily_status = sync_user_daily_status(current_user.id, today)
    progress = ProgresHarian.query.filter_by(user_id=current_user.id, tanggal=today).first()
    mission_run = DailyMissionRun.query.filter_by(user_id=current_user.id, tanggal=today).first()

    if (progress and progress.status_selesai) or (mission_run and mission_run.status_selesai):
        return {'message': 'Misi harian sudah diselesaikan hari ini.'}, 409

    data = request.get_json() or {}
    try:
        score = max(0, int(data.get('score', 0)))
    except (TypeError, ValueError):
        score = 0

    try:
        total_attempts = max(0, int(data.get('total_attempts', 0)))
    except (TypeError, ValueError):
        total_attempts = 0

    try:
        answered_questions = max(0, int(data.get('answered_questions', 0)))
    except (TypeError, ValueError):
        answered_questions = 0

    try:
        total_questions = max(0, int(data.get('total_questions', 0)))
    except (TypeError, ValueError):
        total_questions = DAILY_MISSION_TOTAL_QUESTIONS

    timeout_reached = bool(data.get('timeout_reached', False))

    payload_question_ids = data.get('question_ids') or []
    if not isinstance(payload_question_ids, list):
        payload_question_ids = []

    payload_question_ids = [
        int(item) for item in payload_question_ids
        if str(item).isdigit()
    ]

    if not progress:
        progress = ProgresHarian(user_id=current_user.id, tanggal=today)
        db.session.add(progress)

    if not mission_run:
        mission_run = DailyMissionRun(user_id=current_user.id, tanggal=today)
        db.session.add(mission_run)

    progress.xp_earned = max(int(progress.xp_earned or 0), score)
    progress.status_selesai = True

    total_questions = max(total_questions, answered_questions, score)
    answered_questions = min(answered_questions, total_questions)

    mission_run.total_questions = total_questions
    mission_run.answered_questions = answered_questions
    mission_run.correct_answers = min(score, total_questions)
    mission_run.total_attempts = total_attempts
    mission_run.timeout_reached = timeout_reached
    mission_run.status_selesai = True
    mission_run.completed_at = datetime.utcnow()
    daily_status.mission_completed = True

    session_question_ids = session.get('daily_mission_question_ids') or []
    session_question_date = session.get('daily_mission_question_date')
    if session_question_date != today.isoformat():
        session_question_ids = []

    history_question_ids = session_question_ids or payload_question_ids

    for question_id in history_question_ids:
        already_logged = UserHistory.query.filter_by(
            user_id=current_user.id,
            question_id=question_id,
            date=today
        ).first()
        if already_logged:
            continue
        db.session.add(UserHistory(
            user_id=current_user.id,
            question_id=question_id,
            date=today
        ))

    yesterday = today - timedelta(days=1)
    yesterday_progress = ProgresHarian.query.filter_by(user_id=current_user.id, tanggal=yesterday).first()
    if yesterday_progress and yesterday_progress.status_selesai:
        progress.streak = yesterday_progress.streak + 1
    else:
        progress.streak = 1

    # Bonus streak tetap dipertahankan untuk pengalaman gamifikasi harian.
    progress.bonus = progress.streak * 2

    gained_xp = score + progress.bonus
    if gained_xp > 0:
        current_user.xp += gained_xp
        db.session.add(Skor(user_id=current_user.id, xp_didapat=gained_xp, tanggal=datetime.utcnow()))

    sync_user_level_from_completed_games(current_user)
    session['play_completion_audio'] = bool(not daily_status.completion_audio_played)

    db.session.commit()
    session.pop('daily_mission_question_ids', None)
    session.pop('daily_mission_question_date', None)

    socketio.emit('xp_update', {'xp': current_user.xp, 'level': current_user.level, 'streak': progress.streak, 'bonus': progress.bonus}, to=str(current_user.id))

    return {
        'message': 'Misi harian tersimpan.',
        'xp': current_user.xp,
        'level': current_user.level,
        'streak': progress.streak,
        'bonus': progress.bonus,
        'status_selesai': True,
        'play_completion_audio': bool(not daily_status.completion_audio_played),
        'total_attempts': mission_run.total_attempts,
        'answered_questions': mission_run.answered_questions,
        'correct_answers': mission_run.correct_answers
    }

@main.route('/api/game-questions/<category>')
@login_required
def api_game_questions(category):
    """Berikan daftar soal untuk kategori game tertentu."""
    valid_categories = ['huruf', 'angka', 'warna', 'bentuk', 'bentuk_bangun_ruang', 'warna-bentuk', 'campuran']
    if category not in valid_categories:
        return {'questions': []}

    if category in ['warna-bentuk', 'warna']:
        questions = Soal.query.filter(Soal.kategori.in_(['warna', 'bentuk', 'warna_bentuk', 'bentuk_bangun_ruang'])).all()
    elif category in ['bentuk', 'bentuk_bangun_ruang']:
        questions = Soal.query.filter(Soal.kategori.in_(['bentuk', 'bentuk_bangun_ruang'])).all()
    else:
        questions = Soal.query.filter_by(kategori=category).all()

    if not questions:
        # fallback: berikan beberapa soal umum jika belum ada soal kategori
        questions = Soal.query.limit(10).all()

    random.shuffle(questions)
    return {'questions': [q.to_dict() for q in questions[:5]]}


@main.route('/api/game/huruf/start')
@login_required
def api_game_huruf_start():
    played_today = bool(find_today_gameplay(current_user.id, 'huruf'))
    questions = get_daily_huruf_questions_public()

    if not played_today:
        start_game_history(current_user.id, 'huruf', 25)
        set_progress_status(current_user.id, 'huruf', 'sedang')
        db.session.commit()

    return {
        'played_today': played_today,
        'rules': HURUF_LEVEL_RULES,
        'questions': questions
    }


@main.route('/api/game/huruf/submit-answer', methods=['POST'])
@login_required
def api_game_huruf_submit_answer():
    data = request.get_json() or {}
    question_id = (data.get('question_id') or '').strip()
    selected_answer = (data.get('selected_answer') or '').strip()

    if not question_id or not selected_answer:
        return {'message': 'Data jawaban tidak lengkap.'}, 400

    question = find_huruf_question(question_id)
    if not question:
        return {'message': 'Soal tidak ditemukan untuk hari ini.'}, 404

    is_correct = selected_answer == question['answer']
    return {
        'question_id': question_id,
        'is_correct': is_correct,
        'correct_answer': question['answer'],
        'feedback': 'Jawaban Anda benar' if is_correct else 'Jawaban Anda salah, silakan coba lagi',
        'weight': question['weight'],
        'level': question['level']
    }


@main.route('/api/game/huruf/finish', methods=['POST'])
@login_required
def api_game_huruf_finish():
    data = request.get_json() or {}
    level_scores = data.get('level_scores') or []

    if not isinstance(level_scores, list) or len(level_scores) != len(HURUF_LEVEL_RULES):
        return {'message': 'Format skor level tidak valid.'}, 400

    if find_today_gameplay(current_user.id, 'huruf'):
        return {
            'message': 'Game ini sudah dimainkan hari ini, silakan coba lagi besok.',
            'played_today': True
        }, 409

    sanitized_scores = []
    for value in level_scores:
        try:
            score = int(value)
        except (TypeError, ValueError):
            score = 0
        sanitized_scores.append(max(0, score))

    today = date.today()
    total_score = sum(sanitized_scores)

    for index, score in enumerate(sanitized_scores, start=1):
        db.session.add(GameSession(
            user_id=current_user.id,
            game_name='huruf',
            level=index,
            skor=score,
            tanggal=today,
            created_at=datetime.utcnow()
        ))
        db.session.add(Skor(user_id=current_user.id, xp_didapat=score, tanggal=datetime.utcnow()))

    db.session.add(GamePlay(
        user_id=current_user.id,
        user_name=(current_user.name or current_user.username or 'Belum ada'),
        game_name='huruf',
        score=total_score,
        played_date=today,
        played_at=datetime.utcnow()
    ))

    set_progress_status(current_user.id, 'huruf', 'selesai')
    complete_game_history(current_user.id, 'huruf', total_questions=25, score=total_score)
    db.session.add(UserScore(user_id=current_user.id, game_id='huruf', skor=total_score, tanggal=today, created_at=datetime.utcnow()))
    sync_user_level_from_completed_games(current_user)
    ensure_day6_certificate(current_user)

    db.session.commit()

    return {
        'message': 'Sesi game huruf berhasil disimpan.',
        'played_today': True,
        'total_score': total_score,
        'level_scores': sanitized_scores
    }


@main.route('/api/game/angka/start')
@login_required
def api_game_angka_start():
    played_today = bool(find_today_gameplay(current_user.id, 'angka'))
    questions = get_daily_angka_questions_public()

    if not played_today:
        start_game_history(current_user.id, 'angka', 25)
        set_progress_status(current_user.id, 'angka', 'sedang')
        db.session.commit()

    return {
        'played_today': played_today,
        'rules': ANGKA_LEVEL_RULES,
        'questions': questions
    }


@main.route('/api/game/angka/submit-answer', methods=['POST'])
@login_required
def api_game_angka_submit_answer():
    data = request.get_json() or {}
    question_id = (data.get('question_id') or '').strip()
    selected_answer = (data.get('selected_answer') or '').strip()

    if not question_id or not selected_answer:
        return {'message': 'Data jawaban tidak lengkap.'}, 400

    question = find_angka_question(question_id)
    if not question:
        return {'message': 'Soal tidak ditemukan untuk hari ini.'}, 404

    is_correct = selected_answer == question['answer']
    return {
        'question_id': question_id,
        'is_correct': is_correct,
        'correct_answer': question['answer'],
        'feedback': 'Jawaban Anda benar' if is_correct else 'Jawaban Anda salah, silakan coba lagi',
        'weight': question['weight'],
        'level': question['level']
    }


@main.route('/api/game/angka/finish', methods=['POST'])
@login_required
def api_game_angka_finish():
    data = request.get_json() or {}
    level_scores = data.get('level_scores') or []

    if not isinstance(level_scores, list) or len(level_scores) != len(ANGKA_LEVEL_RULES):
        return {'message': 'Format skor level tidak valid.'}, 400

    if find_today_gameplay(current_user.id, 'angka'):
        return {
            'message': 'Game ini sudah dimainkan hari ini, silakan coba lagi besok.',
            'played_today': True
        }, 409

    sanitized_scores = []
    for value in level_scores:
        try:
            score = int(value)
        except (TypeError, ValueError):
            score = 0
        sanitized_scores.append(max(0, score))

    today = date.today()
    total_score = sum(sanitized_scores)

    for index, score in enumerate(sanitized_scores, start=1):
        db.session.add(GameSession(
            user_id=current_user.id,
            game_name='angka',
            level=index,
            skor=score,
            tanggal=today,
            created_at=datetime.utcnow()
        ))
        db.session.add(Skor(user_id=current_user.id, xp_didapat=score, tanggal=datetime.utcnow()))

    db.session.add(GamePlay(
        user_id=current_user.id,
        user_name=(current_user.name or current_user.username or 'Belum ada'),
        game_name='angka',
        score=total_score,
        played_date=today,
        played_at=datetime.utcnow()
    ))

    set_progress_status(current_user.id, 'angka', 'selesai')
    complete_game_history(current_user.id, 'angka', total_questions=25, score=total_score)
    db.session.add(UserScore(user_id=current_user.id, game_id='angka', skor=total_score, tanggal=today, created_at=datetime.utcnow()))
    current_user.xp += total_score
    sync_user_level_from_completed_games(current_user)
    ensure_day6_certificate(current_user)

    db.session.commit()

    socketio.emit('xp_update', {'xp': current_user.xp, 'level': current_user.level}, to=str(current_user.id))

    return {
        'message': 'Sesi game angka berhasil disimpan.',
        'played_today': True,
        'total_score': total_score,
        'level_scores': sanitized_scores
    }


@main.route('/api/game/warna-bentuk/start')
@login_required
def api_game_warna_bentuk_start():
    played_today = bool(find_today_gameplay(current_user.id, 'warna'))
    questions = get_daily_warna_bentuk_questions_public()

    if not played_today:
        start_game_history(current_user.id, 'warna', 25)
        set_progress_status(current_user.id, 'warna', 'sedang')
        db.session.commit()

    return {
        'played_today': played_today,
        'rules': WARNA_BENTUK_LEVEL_RULES,
        'questions': questions
    }


@main.route('/api/game/warna-bentuk/submit-answer', methods=['POST'])
@login_required
def api_game_warna_bentuk_submit_answer():
    data = request.get_json() or {}
    question_id = (data.get('question_id') or '').strip()
    selected_answer = (data.get('selected_answer') or '').strip()

    if not question_id or not selected_answer:
        return {'message': 'Data jawaban tidak lengkap.'}, 400

    question = find_warna_bentuk_question(question_id)
    if not question:
        return {'message': 'Soal tidak ditemukan untuk hari ini.'}, 404

    is_correct = selected_answer == question['answer']
    return {
        'question_id': question_id,
        'is_correct': is_correct,
        'correct_answer': question['answer'],
        'feedback': 'Jawaban Anda benar' if is_correct else 'Jawaban Anda salah, silakan coba lagi',
        'weight': question['weight'],
        'level': question['level']
    }


@main.route('/api/game/warna-bentuk/finish', methods=['POST'])
@login_required
def api_game_warna_bentuk_finish():
    data = request.get_json() or {}
    level_scores = data.get('level_scores') or []

    if not isinstance(level_scores, list) or len(level_scores) != len(WARNA_BENTUK_LEVEL_RULES):
        return {'message': 'Format skor level tidak valid.'}, 400

    if find_today_gameplay(current_user.id, 'warna'):
        return {
            'message': 'Game ini sudah dimainkan hari ini, silakan coba lagi besok.',
            'played_today': True
        }, 409

    sanitized_scores = []
    for value in level_scores:
        try:
            score = int(value)
        except (TypeError, ValueError):
            score = 0
        sanitized_scores.append(max(0, score))

    today = date.today()
    total_score = sum(sanitized_scores)

    for index, score in enumerate(sanitized_scores, start=1):
        db.session.add(GameSession(
            user_id=current_user.id,
            game_name='warna',
            level=index,
            skor=score,
            tanggal=today,
            created_at=datetime.utcnow()
        ))
        db.session.add(Skor(user_id=current_user.id, xp_didapat=score, tanggal=datetime.utcnow()))

    db.session.add(GamePlay(
        user_id=current_user.id,
        user_name=(current_user.name or current_user.username or 'Belum ada'),
        game_name='warna',
        score=total_score,
        played_date=today,
        played_at=datetime.utcnow()
    ))

    set_progress_status(current_user.id, 'warna', 'selesai')
    complete_game_history(current_user.id, 'warna', total_questions=25, score=total_score)
    db.session.add(UserScore(user_id=current_user.id, game_id='warna', skor=total_score, tanggal=today, created_at=datetime.utcnow()))
    current_user.xp += total_score
    sync_user_level_from_completed_games(current_user)
    ensure_day6_certificate(current_user)

    db.session.commit()

    socketio.emit('xp_update', {'xp': current_user.xp, 'level': current_user.level}, to=str(current_user.id))

    return {
        'message': 'Sesi game warna dan bentuk berhasil disimpan.',
        'played_today': True,
        'total_score': total_score,
        'level_scores': sanitized_scores
    }

@main.route('/game/submit', methods=['POST'])
@login_required
def game_submit():
    """Terima XP dari game interaktif dan update profil user."""
    data = request.get_json() or {}
    xp = int(data.get('xp', 0))
    score = int(data.get('score', xp))
    game_key = normalize_game_key(data.get('game_key'))

    if game_key not in GAME_KEYS:
        return {'message': 'Game tidak valid'}, 400

    if xp < 0:
        xp = 0
    if score < 0:
        score = 0

    existing_today = find_today_gameplay(current_user.id, game_key)
    if existing_today:
        return {
            'message': 'Game ini sudah dimainkan hari ini, silakan coba lagi besok.',
            'played_today': True,
            'score': existing_today.score
        }, 409

    db.session.add(GamePlay(
        user_id=current_user.id,
        user_name=current_user.name,
        game_name=game_key,
        score=score,
        played_date=date.today(),
        played_at=datetime.utcnow()
    ))

    set_progress_status(current_user.id, game_key, 'selesai')
    complete_game_history(current_user.id, game_key, total_questions=5, score=score)
    db.session.add(UserScore(user_id=current_user.id, game_id=game_key, skor=score, tanggal=date.today(), created_at=datetime.utcnow()))

    if xp > 0:
        current_user.xp += xp
        db.session.add(Skor(user_id=current_user.id, xp_didapat=xp, tanggal=datetime.utcnow()))

        # Berikan badge otomatis berdasarkan pencapaian level
        earned_badges = Badge.query.filter(Badge.level_minimum <= current_user.level).all()
        for badge in earned_badges:
            existing = UserBadge.query.filter_by(user_id=current_user.id, badge_id=badge.id).first()
            if not existing:
                db.session.add(UserBadge(user_id=current_user.id, badge_id=badge.id))

    sync_user_level_from_completed_games(current_user)
    ensure_day6_certificate(current_user)

    db.session.commit()
    if xp > 0:
        socketio.emit('xp_update', {'xp': current_user.xp, 'level': current_user.level}, to=str(current_user.id))

    return {
        'xp': current_user.xp,
        'level': current_user.level,
        'played_today': True,
        'score': score,
        'game_key': game_key
    }


@main.route('/api/game-daily-status')
@login_required
def api_game_daily_status():
    today = date.today()
    rows = GamePlay.query.filter_by(user_id=current_user.id, played_date=today).all()
    row_map = {r.game_name: r for r in rows}

    result = {}
    for key in GAME_KEYS:
        row = row_map.get(key)
        result[key] = {
            'played_today': bool(row),
            'status_text': 'Sudah dimainkan hari ini' if row else 'Bisa dimainkan hari ini',
            'score': row.score if row else 0,
            'played_date': today.isoformat()
        }

    return {'games': result}


@main.route('/api/game/daily-summary')
@login_required
def api_game_daily_summary():
    """Return per-game answered_questions (from UserGameHistory) and score (from GamePlay) for today."""
    today = date.today()
    keys = ['huruf', 'angka', 'warna']
    out = {}
    for key in keys:
        history = UserGameHistory.query.filter_by(user_id=current_user.id, game_id=key, tanggal_main=today).first()
        correct = int(history.answered_questions or 0) if history else 0
        gp = GamePlay.query.filter_by(user_id=current_user.id, game_name=key, played_date=today).first()
        score = int(gp.score or 0) if gp else 0
        out[key] = {'correct': correct, 'score': score}

    adventure_points_today = int(
        db.session.query(func.coalesce(func.sum(GamePlay.score), 0))
        .filter(
            GamePlay.user_id == current_user.id,
            GamePlay.played_date == today,
            GamePlay.game_name.in_(ADVENTURE_GAMES)
        )
        .scalar() or 0
    )
    if adventure_points_today > 0:
        badge_stars = min(5, ((adventure_points_today - 1) // 45) + 1)
    else:
        badge_stars = 0

    badge_label = f"{'⭐' * badge_stars} {badge_stars} Bintang" if badge_stars > 0 else 'Belum ada badge'

    return {
        'games': out,
        'total_adventure_points': adventure_points_today,
        'adventure_badge_stars': badge_stars,
        'adventure_badge_label': badge_label
    }


@main.route('/api/game/progress/update', methods=['POST'])
@login_required
def api_game_progress_update():
    data = request.get_json() or {}
    game_key = normalize_game_key(data.get('game_key'))
    answered_questions = data.get('answered_questions')
    total_questions = data.get('total_questions')
    status = data.get('status')

    if game_key not in ADVENTURE_GAMES:
        return {'message': 'Game tidak valid.'}, 400

    update_game_history_progress(
        current_user.id,
        game_key,
        answered_questions=answered_questions,
        total_questions=total_questions,
        status=status if status in ['belum', 'sedang', 'selesai'] else None
    )

    if status == 'sedang':
        set_progress_status(current_user.id, game_key, 'sedang')
    elif status == 'selesai':
        set_progress_status(current_user.id, game_key, 'selesai')

    db.session.commit()
    return {'message': 'Progress game diperbarui.'}


@main.route('/api/leaderboard-harian')
@login_required
def api_leaderboard_harian():
    today = date.today()
    leaders = build_daily_leaderboard(today)
    current_entry = next((item for item in leaders if item['user_id'] == current_user.id), None)
    return {
        'tanggal': today.isoformat(),
        'leaders': leaders,
        'current': current_entry
    }


@main.route('/api/certificates')
@login_required
def api_certificates():
    ensure_day6_certificate(current_user)
    db.session.commit()

    certs = UserCertificate.query.filter_by(user_id=current_user.id).order_by(UserCertificate.issue_date.desc()).all()
    return {
        'certificates': [
            {
                'id': cert.id,
                'type': cert.certificate_type,
                'issue_date': cert.issue_date.isoformat(),
                'score': cert.score_snapshot,
                'message': cert.message,
                'view_url': url_for('main.view_certificate', certificate_id=cert.id),
                'download_url': url_for('main.download_certificate', certificate_id=cert.id)
            } for cert in certs
        ]
    }


@main.route('/certificate/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    cert = UserCertificate.query.filter_by(id=certificate_id, user_id=current_user.id).first_or_404()
    svg = build_certificate_svg(current_user, cert)
    return Response(svg, mimetype='image/svg+xml')


@main.route('/certificate/<int:certificate_id>/download')
@login_required
def download_certificate(certificate_id):
    cert = UserCertificate.query.filter_by(id=certificate_id, user_id=current_user.id).first_or_404()
    svg = build_certificate_svg(current_user, cert)
    return Response(
        svg,
        mimetype='image/svg+xml',
        headers={
            'Content-Disposition': f'attachment; filename=sertifikat-{current_user.username}-{certificate_id}.svg'
        }
    )


@main.route('/api/adventure-progress')
@login_required
def api_adventure_progress():
    return {'progress': get_user_adventure_progress(current_user.id)}


@main.route('/api/adventure-progress/start', methods=['POST'])
@login_required
def api_adventure_progress_start():
    data = request.get_json() or {}
    game_key = normalize_game_key(data.get('game_key'))

    if game_key not in ADVENTURE_GAMES:
        return {'message': 'Game tidak valid.'}, 400

    set_progress_status(current_user.id, game_key, 'sedang')
    db.session.commit()
    return {'message': 'Progress game ditandai sedang dimainkan.'}


@main.route('/api/adventure-progress/complete', methods=['POST'])
@login_required
def api_adventure_progress_complete():
    data = request.get_json() or {}
    game_key = normalize_game_key(data.get('game_key'))

    if game_key not in ADVENTURE_GAMES:
        return {'message': 'Game tidak valid.'}, 400

    set_progress_status(current_user.id, game_key, 'selesai')
    db.session.commit()
    return {'message': 'Progress game ditandai selesai.'}


@main.route('/api/access-time-status')
@login_required
def api_access_time_status():
    status = get_access_status_for_user(current_user)
    return {
        'allowed_now': status['allowed_now'],
        'is_limited': status['is_limited'],
        'start_time': format_hhmm(status['start']),
        'end_time': format_hhmm(status['end']),
        'message': status['message']
    }

@main.route('/menu')
@login_required
def menu():
    if current_user.role == 'admin':
        flash('Access denied! Admin tidak bisa mengakses menu pengguna.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()
    daily_status = sync_user_daily_status(current_user.id, today)
    progress_today = ProgresHarian.query.filter_by(user_id=current_user.id, tanggal=today).first()
    mission_run_today = DailyMissionRun.query.filter_by(user_id=current_user.id, tanggal=today).first()
    mission_complete = bool(
        (progress_today and progress_today.status_selesai) or
        (mission_run_today and mission_run_today.status_selesai)
    )
    daily_status.mission_completed = mission_complete
    
    # Logika yang benar: hanya play audio jika:
    # 1. Misi belum selesai (mission_complete = false)
    # 2. Dan reminder belum pernah diputar hari ini (reminder_played = false)
    # 3. Dan ada request dari session (session.pop mengembalikan true) ATAU kondisi di atas terpenuhi
    mission_not_complete = not mission_complete
    reminder_not_played = not daily_status.reminder_played
    
    # Cek apakah ada request dari session untuk memainkan audio
    session_has_audio_request = session.pop('play_login_mission_audio', False)
    
    # Hanya play jika misi belum selesai DAN reminder belum diputar
    # Dan ada request dari session ATAU kondisi misi belum selesai dan reminder belum diputar
    play_login_mission_audio = session_has_audio_request or (mission_not_complete and reminder_not_played)
    play_login_mission_audio = play_login_mission_audio and mission_not_complete and reminder_not_played
    
    play_completion_audio = (mission_complete and not daily_status.completion_audio_played) or bool(session.pop('play_completion_audio', False))
    db.session.commit()

    # Jika mission_complete masih false, cek apakah ada progress periode hari ini yang diawali karena misi harian (misal target xp sudah tercapai)
    # Already done by ProgresHarian.status_selesai

    return render_template(
        'menu.html',
        mission_complete=mission_complete,
        play_login_mission_audio=play_login_mission_audio,
        play_completion_audio=bool(play_completion_audio and mission_complete and not daily_status.completion_audio_played),
        today_iso=today.isoformat()
    )


@main.route('/mulai')
@login_required
def mulai():
    """Navigasi tombol Mulai ke daftar game/peta petualangan."""
    return redirect(url_for('main.peta_pertualangan'))

@main.route('/progres-harian')
@login_required
def progres_harian():
    if current_user.role == 'admin':
        flash('Access denied! Admin tidak bisa mengakses progres harian pengguna.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()
    grant_daily_login_star(current_user.id)
    ensure_day6_certificate(current_user)
    sync_user_level_from_completed_games(current_user)
    db.session.commit()

    # 1. Total bintang dari login harian
    total_stars = get_total_stars(current_user.id)

    # 2. Game terselesaikan hari ini
    games_completed = GamePlay.query.filter_by(user_id=current_user.id, played_date=today).count()

    # 2a. Total poin peta pertualangan hari ini
    adventure_points_today = int(
        db.session.query(func.coalesce(func.sum(GamePlay.score), 0))
        .filter(
            GamePlay.user_id == current_user.id,
            GamePlay.played_date == today,
            GamePlay.game_name.in_(ADVENTURE_GAMES)
        )
        .scalar() or 0
    )
    if adventure_points_today > 0:
        badge_stars = min(5, ((adventure_points_today - 1) // 45) + 1)
    else:
        badge_stars = 0

    badge_display = '⭐' * badge_stars if badge_stars > 0 else 'Belum ada'
    badge_points = adventure_points_today

    # 3. Daily progress per game dari user_game_history
    materi_categories = [
        ('huruf', 'A. Mengenal Huruf'),
        ('angka', 'B. Mengenal Angka'),
        ('warna', 'C. Mengenal Warna dan Bentuk Bangun Ruang')
    ]

    daily_progress = []
    for category_key, category_name in materi_categories:
        history = UserGameHistory.query.filter_by(
            user_id=current_user.id,
            game_id=category_key,
            tanggal_main=today
        ).first()

        if not history:
            percentage = 0
        elif history.status == 'selesai':
            percentage = 100
        elif (history.total_questions or 0) > 0:
            percentage = int(min(100, (history.answered_questions / history.total_questions) * 100))
        else:
            percentage = 0

        daily_progress.append({
            'materi_name': category_name,
            'percentage': min(percentage, 100)
        })

    # 4. Total soal dikerjakan = semua game + misi harian
    game_questions_answered = int(
        db.session.query(func.coalesce(func.sum(UserGameHistory.answered_questions), 0))
        .filter(UserGameHistory.user_id == current_user.id)
        .scalar() or 0
    )
    mission_questions_answered = int(
        db.session.query(func.coalesce(func.sum(DailyMissionRun.answered_questions), 0))
        .filter(DailyMissionRun.user_id == current_user.id, DailyMissionRun.status_selesai.is_(True))
        .scalar() or 0
    )
    total_questions = game_questions_answered + mission_questions_answered

    # 5. Login consistency dari user_daily_login
    login_consistency = 0
    check_date = today
    for _ in range(365):
        login_row = UserDailyLogin.query.filter_by(
            user_id=current_user.id,
            tanggal=check_date,
            bintang_didapat=True
        ).first()
        if login_row:
            login_consistency += 1
            check_date -= timedelta(days=1)
        else:
            break

    # 6. Sertifikat dari user_certificates
    cert_rows = UserCertificate.query.filter_by(user_id=current_user.id).order_by(UserCertificate.issue_date.desc()).all()
    certificates = []
    for cert in cert_rows:
        certificates.append({
            'badge_name': cert.certificate_type,
            'badge_description': cert.message
        })

    certificates_count = len(certificates)

    # 7. User's rank dari leaderboard
    leaderboard_entries = build_leaderboard_entries()
    user_rank = None
    user_certificate = None
    for entry in leaderboard_entries:
        if entry['user_id'] == current_user.id:
            user_rank = entry['rank']
            user_certificate = entry['certificate']
            break
    
    if user_rank is None:
        user_rank = len(leaderboard_entries) + 1
        user_certificate = get_certificate_name(user_rank)

    return render_template(
        'progres_harian.html',
        total_stars=total_stars,
        games_completed=games_completed,
        user_rank=user_rank,
        user_certificate=user_certificate,
        badge_display=badge_display,
        badge_points=badge_points,
        certificates_count=certificates_count,
        daily_progress=daily_progress,
        total_questions=total_questions,
        login_consistency=login_consistency,
        certificates=certificates
    )

# Peta Petualangan
@main.route('/peta-pertualangan')
@login_required
def peta_pertualangan():
    access_status = get_access_status_for_user(current_user)
    return render_template(
        'peta_pertualangan.html',
        access_allowed=access_status['allowed_now'],
        access_start=format_hhmm(access_status['start']),
        access_end=format_hhmm(access_status['end']),
        access_message=access_status['message'],
        access_is_limited=access_status['is_limited'],
    )

# Materi routes

def youtube_to_embed(url):
    """Convert a YouTube watch/short URL to an embed URL."""
    import re
    if not url:
        return ''
    # Already embed
    if 'youtube.com/embed/' in url:
        return url
    # youtu.be/VIDEO_ID
    m = re.search(r'youtu\.be/([A-Za-z0-9_-]{11})', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'
    # youtube.com/watch?v=VIDEO_ID
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{11})', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'
    return url


def is_valid_youtube_url(url):
    """Return True if url looks like a YouTube link."""
    import re
    return bool(re.search(r'(youtu\.be/|youtube\.com/(watch|embed|shorts))', url or ''))


def is_valid_video_url(url):
    """Return True if URL is a valid absolute http(s) URL and points to a video source we support."""
    from urllib.parse import urlparse

    raw = (url or '').strip()
    if not raw:
        return False

    parsed = urlparse(raw)
    if parsed.scheme not in ('http', 'https'):
        return False
    if not parsed.netloc:
        return False

    host = parsed.netloc.lower()
    if host.startswith('www.'):
        host = host[4:]

    # Saat ini materi ditampilkan sebagai link video eksternal, minimum dukung YouTube.
    if host in ('youtube.com', 'youtu.be', 'm.youtube.com'):
        return is_valid_youtube_url(raw)

    return False


@main.route('/guru-dashboard/materi/tambah', methods=['POST'])
@login_required
def guru_tambah_materi():
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    judul = request.form.get('judul', '').strip()
    deskripsi = request.form.get('deskripsi', '').strip()
    link_youtube = request.form.get('link_youtube', '').strip()
    kategori = request.form.get('kategori', '').strip()

    if not judul or not link_youtube:
        flash('Judul dan link video wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-materi')

    if not is_valid_video_url(link_youtube):
        flash('Link video tidak valid. Gunakan URL YouTube yang benar (https://www.youtube.com/watch?v=... atau https://youtu.be/...).', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-materi')

    new_materi = Materi(
        judul=judul,
        deskripsi=deskripsi or None,
        link_youtube=link_youtube,
        kategori=kategori or None,
    )
    db.session.add(new_materi)
    db.session.commit()
    flash(f'Materi "{judul}" berhasil ditambahkan.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-materi')


@main.route('/guru-dashboard/materi/edit/<int:materi_id>', methods=['POST'])
@login_required
def guru_edit_materi(materi_id):
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    materi_obj = Materi.query.get_or_404(materi_id)
    judul = request.form.get('judul', '').strip()
    deskripsi = request.form.get('deskripsi', '').strip()
    link_youtube = request.form.get('link_youtube', '').strip()
    kategori = request.form.get('kategori', '').strip()

    if not judul or not link_youtube:
        flash('Judul dan link video wajib diisi.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-materi')

    if not is_valid_video_url(link_youtube):
        flash('Link video tidak valid. Gunakan URL YouTube yang benar.', 'danger')
        return redirect(url_for('main.guru_dashboard') + '#tab-materi')

    materi_obj.judul = judul
    materi_obj.deskripsi = deskripsi or None
    materi_obj.link_youtube = link_youtube
    materi_obj.kategori = kategori or None
    db.session.commit()
    flash(f'Materi "{judul}" berhasil diperbarui.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-materi')


@main.route('/guru-dashboard/materi/hapus/<int:materi_id>', methods=['POST'])
@login_required
def guru_hapus_materi(materi_id):
    if current_user.role not in ['guru', 'admin']:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.guru_dashboard'))

    materi_obj = Materi.query.get_or_404(materi_id)
    judul = materi_obj.judul
    db.session.delete(materi_obj)
    db.session.commit()
    flash(f'Materi "{judul}" berhasil dihapus.', 'success')
    return redirect(url_for('main.guru_dashboard') + '#tab-materi')


@main.route('/materi')
@login_required
def materi():
    materi_list = Materi.query.order_by(Materi.created_at.asc()).all()
    materi_data = [
        {
            'id': m.id,
            'judul': m.judul,
            'deskripsi': m.deskripsi,
            'link_youtube': m.link_youtube,
            'embed_url': youtube_to_embed(m.link_youtube),
            'kategori': m.kategori,
            'created_at': m.created_at,
        }
        for m in materi_list
    ]
    return render_template('materi.html', materi_list=materi_data)

@main.route('/materi/huruf')
@login_required
def materi_huruf():
    return render_template('materi_huruf.html')

# Game routes
@main.route('/game/huruf')
@login_required
def game_huruf():
    blocked = enforce_game_access_time_or_redirect()
    if blocked:
        return blocked

    if find_today_gameplay(current_user.id, 'huruf'):
        flash('Game ini sudah dimainkan hari ini, silakan coba lagi besok.', 'warning')
        return redirect(url_for('main.peta_pertualangan'))

    start_game_history(current_user.id, 'huruf', 25)
    set_progress_status(current_user.id, 'huruf', 'sedang')
    db.session.commit()
    return render_template('game_huruf.html')

@main.route('/game/angka')
@login_required
def game_angka():
    blocked = enforce_game_access_time_or_redirect()
    if blocked:
        return blocked

    if find_today_gameplay(current_user.id, 'angka'):
        flash('Game ini sudah dimainkan hari ini, silakan coba lagi besok.', 'warning')
        return redirect(url_for('main.peta_pertualangan'))

    start_game_history(current_user.id, 'angka', 25)
    set_progress_status(current_user.id, 'angka', 'sedang')
    db.session.commit()
    return render_template('game_angka.html')

@main.route('/game/warna-bentuk')
@login_required
def game_warna_bentuk():
    blocked = enforce_game_access_time_or_redirect()
    if blocked:
        return blocked

    if find_today_gameplay(current_user.id, 'warna'):
        flash('Game ini sudah dimainkan hari ini, silakan coba lagi besok.', 'warning')
        return redirect(url_for('main.peta_pertualangan'))

    start_game_history(current_user.id, 'warna', 25)
    set_progress_status(current_user.id, 'warna', 'sedang')
    db.session.commit()
    return render_template('game_warna_bentuk.html')

@main.route('/materi/angka')
@login_required
def materi_angka():
    return render_template('materi_angka.html')

@main.route('/materi/warna-bentuk')
@login_required
def materi_warna_bentuk():
    return render_template('materi_warna_bentuk.html')

@main.route('/api/xp-data')
@login_required
def api_xp_data():
    if current_user.role not in ['guru', 'orangtua', 'admin']:
        return {'error': 'Access denied'}, 403

    if current_user.role == 'orangtua':
        child_ids = [row.student_id for row in ParentStudent.query.filter_by(parent_id=current_user.id).all()]
        anak_users = []
        if child_ids:
            anak_users = (
                User.query
                .filter(User.id.in_(child_ids))
                .filter(func.lower(User.role).in_(STUDENT_ROLES))
                .all()
            )
    else:
        anak_users = User.query.filter(func.lower(User.role).in_(STUDENT_ROLES)).all()

    labels = []
    datasets = []

    # Get last 7 days
    today = date.today()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%Y-%m-%d'))

    for user in anak_users:
        data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            # Sum XP earned on that day
            skor = Skor.query.filter_by(user_id=user.id).filter(Skor.tanggal >= day, Skor.tanggal < day + timedelta(days=1)).all()
            xp = sum(s.xp_didapat for s in skor)
            data.append(xp)
        datasets.append({
            'label': user.name,
            'data': data,
            'borderColor': 'rgb(' + str(random.randint(0,255)) + ',' + str(random.randint(0,255)) + ',' + str(random.randint(0,255)) + ')',
            'fill': False
        })

    return {'labels': labels, 'datasets': datasets}

@main.route('/api/xp-data-orangtua')
@login_required
def api_xp_data_orangtua():
    return api_xp_data()  # Same as guru for now

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# SocketIO events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(str(current_user.id))

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(str(current_user.id))

