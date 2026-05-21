"""
Model untuk audit log dan validasi soal.
"""
from app import db
from datetime import datetime
from enum import Enum

class SoalChangeType(Enum):
    """Tipe perubahan soal"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    VALIDATED = "validated"
    LOCKED = "locked"
    UNLOCKED = "unlocked"

class SoalAuditLog(db.Model):
    """Model untuk mencatat setiap perubahan soal"""
    
    __tablename__ = 'soal_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    soal_id = db.Column(db.Integer, db.ForeignKey('soal.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    change_type = db.Column(db.String(50), nullable=False)  # created, updated, deleted, validated
    old_data = db.Column(db.JSON, nullable=True)  # Data sebelum perubahan (untuk update)
    new_data = db.Column(db.JSON, nullable=True)  # Data sesudah perubahan
    change_reason = db.Column(db.Text, nullable=True)  # Alasan perubahan
    ip_address = db.Column(db.String(45), nullable=True)  # IP address user
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    soal = db.relationship('Soal', backref=db.backref('audit_logs', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('soal_changes', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SoalAuditLog {self.id}: soal_id={self.soal_id} {self.change_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'soal_id': self.soal_id,
            'user_id': self.user_id,
            'change_type': self.change_type,
            'old_data': self.old_data,
            'new_data': self.new_data,
            'change_reason': self.change_reason,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SoalProtection(db.Model):
    """Model untuk proteksi soal dari perubahan tidak sengaja"""
    
    __tablename__ = 'soal_protection'
    
    id = db.Column(db.Integer, primary_key=True)
    soal_id = db.Column(db.Integer, db.ForeignKey('soal.id'), unique=True, nullable=False, index=True)
    is_locked = db.Column(db.Boolean, default=False, index=True)  # Lock soal dari edit/delete
    is_validated = db.Column(db.Boolean, default=False, index=True)  # Soal sudah diverifikasi benar
    validation_errors = db.Column(db.JSON, nullable=True)  # Error validasi jika ada
    locked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    locked_at = db.Column(db.DateTime, nullable=True)
    locked_reason = db.Column(db.Text, nullable=True)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    soal = db.relationship('Soal', backref=db.backref('protection', uselist=False, cascade='all, delete-orphan'))
    locked_by = db.relationship('User', foreign_keys=[locked_by_id], backref=db.backref('locked_soals', lazy='dynamic'))
    validated_by = db.relationship('User', foreign_keys=[validated_by_id], backref=db.backref('validated_soals', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SoalProtection {self.id}: soal_id={self.soal_id} locked={self.is_locked} validated={self.is_validated}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'soal_id': self.soal_id,
            'is_locked': self.is_locked,
            'is_validated': self.is_validated,
            'validation_errors': self.validation_errors,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'locked_reason': self.locked_reason,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
