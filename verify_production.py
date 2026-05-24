#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-deployment verification script.
Pastikan aplikasi siap untuk production sebelum deploy.
"""

import sys
import os
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main'))

from app import db, create_app

def verify_production_setup():
    """Verify production setup"""
    
    print("\n" + "="*70)
    print("VERIFIKASI PRODUCTION READINESS")
    print("="*70 + "\n")
    
    app = create_app()
    
    with app.app_context():
        checks_passed = 0
        checks_total = 0
        
        # Check 1: Configuration
        print("1. Konfigurasi Aplikasi")
        print("-" * 70)
        checks_total += 1
        
        env_secret = os.environ.get('SECRET_KEY')
        if env_secret and len(env_secret) >= 32:
            print("  [OK] SECRET_KEY: Aman dan cukup panjang")
            checks_passed += 1
        elif env_secret:
            print(f"  [WARN] SECRET_KEY: Terlalu pendek ({len(env_secret)} chars, min 32)")
        else:
            print("  [WARN] SECRET_KEY: Menggunakan default development key")
        
        debug_mode = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
        if not debug_mode:
            print("  [OK] DEBUG: False (production mode)")
            checks_passed += 1
        else:
            print("  [ERROR] DEBUG: True (DANGER - disable untuk production)")
        
        checks_total += 1
        
        # Check 2: Database
        print("\n2. Konfigurasi Database")
        print("-" * 70)
        checks_total += 1
        
        db_url = os.environ.get('DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI', ''))
        if 'sqlite' in db_url.lower():
            print(f"  [WARN] Database: SQLite (cocok untuk dev, perhatikan untuk production)")
            print(f"    Path: {db_url}")
        elif 'postgresql' in db_url.lower():
            print("  [OK] Database: PostgreSQL (recommended)")
            checks_passed += 1
        elif 'mysql' in db_url.lower():
            print("  [OK] Database: MySQL/MariaDB")
            checks_passed += 1
        else:
            print(f"  [ERROR] Database: Unknown type - {db_url}")
        
        checks_total += 1
        
        # Check 3: Database Tables
        print("\n3. Database Tables")
        print("-" * 70)
        checks_total += 1
        
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'soal', 'daily_mission_questions']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if not missing_tables:
                print(f"  [OK] All required tables exist ({len(tables)} total tables)")
                checks_passed += 1
            else:
                print(f"  [ERROR] Missing tables: {', '.join(missing_tables)}")
                print("     Jalankan: python init_db.py")
        except Exception as e:
            print(f"  [ERROR] Database connection error: {e}")
        
        # Check 4: Question Bank
        print("\n4. Question Bank")
        print("-" * 70)
        checks_total += 1
        
        try:
            from app.models.question import Soal
            total_questions = Soal.query.count()
            
            # Check for questions with all 4 options
            questions_missing_d = Soal.query.filter(
                (Soal.pilihan_d.is_(None)) | (Soal.pilihan_d == '')
            ).count()
            
            if total_questions > 0:
                print(f"  [OK] Question Bank: {total_questions} soal tersedia")
                
                if questions_missing_d == 0:
                    print(f"  [OK] All questions have 4 options")
                    checks_passed += 1
                else:
                    print(f"  [ERROR] {questions_missing_d} questions missing option D")
            else:
                print(f"  [WARN] Question Bank: Kosong (init dengan python init_db.py)")
        except Exception as e:
            print(f"  [ERROR] Error checking questions: {e}")
        
        # Check 5: Static Files
        print("\n5. Static Files & Uploads")
        print("-" * 70)
        checks_total += 1
        
        static_path = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main', 'app', 'static')
        uploads_path = os.path.join(static_path, 'uploads', 'question_bank')
        
        if os.path.exists(static_path):
            print(f"  [OK] Static folder exists: {static_path}")
        else:
            print(f"  [WARN] Static folder not found: {static_path}")
        
        if os.path.exists(uploads_path):
            print(f"  [OK] Uploads folder exists and writable")
            checks_passed += 1
        else:
            print(f"  [WARN] Uploads folder: Creating...")
            try:
                os.makedirs(uploads_path, exist_ok=True)
                print(f"  [OK] Created uploads folder")
                checks_passed += 1
            except Exception as e:
                print(f"  [ERROR] Cannot create uploads folder: {e}")
        
        checks_total += 1
        
        # Check 6: Dependencies
        print("\n6. Dependencies")
        print("-" * 70)
        checks_total += 1
        
        required_packages = [
            ('flask', 'Flask'),
            ('gunicorn', 'gunicorn'),
            ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
            ('dotenv', 'python-dotenv'),
        ]
        
        missing_packages = []
        for pkg, display_name in required_packages:
            try:
                __import__(pkg)
            except ImportError:
                missing_packages.append(display_name)
        
        if not missing_packages:
            print(f"  [OK] All required packages installed")
            checks_passed += 1
        else:
            print(f"  [ERROR] Missing packages: {', '.join(missing_packages)}")
            print(f"     Install with: pip install -r requirements.txt")
        
        # Check 7: Authentication
        print("\n7. Authentication System")
        print("-" * 70)
        checks_total += 1
        
        try:
            from app.models.user import User
            admin_count = User.query.filter_by(role='admin').count()
            total_users = User.query.count()
            
            if admin_count > 0:
                print(f"  [OK] Admin user exists ({admin_count} admin, {total_users} total users)")
                checks_passed += 1
            else:
                print(f"  [WARN] No admin user. Create with: python create_admin.py")
        except Exception as e:
            print(f"  [WARN] Could not verify users: {e}")
            # Don't fail on this check, database might not be initialized yet
        
        # Summary
        print("\n" + "="*70)
        print("RINGKASAN")
        print("="*70)
        
        percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0
        print(f"\nStatus: {checks_passed}/{checks_total} checks passed ({percentage:.0f}%)")
        
        if checks_passed == checks_total:
            print("\n[OK] APLIKASI SIAP UNTUK PRODUCTION DEPLOYMENT")
            return 0
        elif checks_passed >= checks_total * 0.8:
            print("\n[WARN] APLIKASI DAPAT DI-DEPLOY TAPI ADA WARNINGS")
            return 0
        else:
            print("\n[ERROR] APLIKASI BELUM SIAP UNTUK DEPLOYMENT")
            print("   Selesaikan items di atas sebelum deploy")
            return 1

if __name__ == '__main__':
    exit_code = verify_production_setup()
    sys.exit(exit_code)
