from flask import Blueprint, jsonify, request, redirect, url_for
from app.models.question import Soal

question_bp = Blueprint('question_bank', __name__)

QUESTION_CATEGORIES = ['huruf', 'angka', 'warna', 'bentuk_bangun_ruang']


def normalize_question_category(raw_category):
    if not raw_category:
        return None
    key = raw_category.strip().lower().replace('-', '_').replace(' ', '_')
    if key in QUESTION_CATEGORIES:
        return key
    if key in ['bentuk', 'bangun_ruang', 'bentuk_bangun']:
        return 'bentuk_bangun_ruang'
    return None


@question_bp.route('/api/question-bank', methods=['GET'])
@question_bp.route('/api/question-bank/<category>', methods=['GET'])
def api_question_bank(category=None):
    category = normalize_question_category(category)
    query = Soal.query.order_by(Soal.created_at.desc(), Soal.id.desc())
    if category:
        query = query.filter_by(kategori=category)
    questions = [row.to_dict() for row in query.all()]
    return jsonify(questions=questions, category=category)


@question_bp.route('/guru-dashboard/kelola-soal/<category>')
def guru_kelola_soal_category(category=None):
    category = normalize_question_category(category)
    if not category:
        return redirect(url_for('main.guru_dashboard') + '#tab-kelola-soal')
    return redirect(url_for('main.guru_dashboard', kelola_kategori=category) + '#tab-kelola-soal')
