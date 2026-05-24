from app import db
from datetime import datetime

class Soal(db.Model):
    """Model untuk soal kuis / game.

    Menyimpan bank soal misi harian dan game.
    Skema utama mengikuti tabel `questions`.
    """

    __tablename__ = 'soal'

    id = db.Column(db.Integer, primary_key=True)
    kategori = db.Column('kategori', db.String(50), nullable=False, default='umum', index=True)
    pertanyaan = db.Column('pertanyaan', db.Text, nullable=False)
    pilihan_a = db.Column('pilihan_a', db.Text, nullable=False)
    pilihan_b = db.Column('pilihan_b', db.Text, nullable=False)
    pilihan_c = db.Column('pilihan_c', db.Text, nullable=False)
    pilihan_d = db.Column('pilihan_d', db.Text, nullable=True)
    question_type = db.Column('question_type', db.String(40), nullable=True)
    image_question = db.Column('image_question', db.Text, nullable=True)
    image_option_a = db.Column('image_option_a', db.Text, nullable=True)
    image_option_b = db.Column('image_option_b', db.Text, nullable=True)
    image_option_c = db.Column('image_option_c', db.Text, nullable=True)
    image_option_d = db.Column('image_option_d', db.Text, nullable=True)
    jawaban_benar = db.Column('jawaban_benar', db.String(16), nullable=False)
    use_in_daily_mission = db.Column(db.Boolean, nullable=False, default=True, index=True)
    use_in_adventure_map = db.Column(db.Boolean, nullable=False, default=True, index=True)
    difficulty = db.Column(db.String(20), nullable=False, default='mudah', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usages = db.relationship('QuestionUsage', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def answer_letter_to_key(value):
        mapping = {
            'A': 'option_a',
            'B': 'option_b',
            'C': 'option_c',
            'D': 'option_d',
        }
        return mapping.get((value or '').strip().upper(), 'option_a')

    @staticmethod
    def answer_key_to_letter(value):
        normalized = (value or '').strip().lower()
        mapping = {
            'a': 'A',
            'b': 'B',
            'c': 'C',
            'd': 'D',
            'option_a': 'A',
            'option_b': 'B',
            'option_c': 'C',
            'option_d': 'D',
        }
        return mapping.get(normalized, 'A')

    def to_dict(self):
        answer_letter = self.answer_key_to_letter(self.jawaban_benar)
        return {
            'id': self.id,
            'kategori': self.kategori,
            'category': self.kategori,
            'difficulty': self.difficulty,
            'prompt': self.pertanyaan,
            'question': self.pertanyaan,
            'option_a': self.pilihan_a,
            'option_b': self.pilihan_b,
            'option_c': self.pilihan_c,
            'option_d': self.pilihan_d,
            'question_type': self.question_type,
            'question_image': self.image_question,
            'option_image_a': self.image_option_a,
            'option_image_b': self.image_option_b,
            'option_image_c': self.image_option_c,
            'option_image_d': self.image_option_d,
            # `answer` dipertahankan agar kompatibel dengan kode lama.
            'answer': self.answer_letter_to_key(answer_letter),
            'correct_answer': answer_letter,
            'answer_key': self.answer_letter_to_key(answer_letter),
            'use_in_daily_mission': bool(self.use_in_daily_mission),
            'use_in_adventure_map': bool(self.use_in_adventure_map),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    # Backwards compatibility properties in case templates still use old field names.
    @property
    def prompt(self):
        return self.pertanyaan

    @property
    def option_a(self):
        return self.pilihan_a

    @property
    def option_b(self):
        return self.pilihan_b

    @property
    def option_c(self):
        return self.pilihan_c

    @property
    def option_d(self):
        return self.pilihan_d

    @property
    def answer(self):
        return self.answer_letter_to_key(self.jawaban_benar)
