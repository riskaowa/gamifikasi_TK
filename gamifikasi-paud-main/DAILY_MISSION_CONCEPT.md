# Konsep Soal Misi Harian

## 1) Sistem Misi Harian
- Setiap user mendapat 2 soal per hari.
- Soal diambil acak dari bank soal database.
- Soal hari yang sama tidak boleh terulang untuk user yang sama.
- Sistem memprioritaskan soal yang belum pernah dikerjakan user.
- Jika soal baru habis, sistem boleh mengulang soal lama dengan jeda cooldown beberapa hari.

## 2) Sumber Materi
Bank soal disusun dari topik video berikut:
- Mengenal huruf: https://youtu.be/TOrYYnGGY_o?si=JXkbPaGn16xVvmxO
- Mengenal angka: https://youtu.be/X3OfM6qsjKQ?si=I7Be_eXnJexpBqL9
- Mengenal warna dan bentuk bangun ruang: https://youtu.be/p0k_TWCMLZ8?si=D_4DC3lYcXWQBRlo

Catatan konten:
- Fokus soal: pengenalan simbol, urutan, pencocokan, dan identifikasi visual sederhana.
- Bahasa soal dibuat pendek, konkret, dan sesuai usia PAUD.

## 3) Struktur Database

### Tabel questions
- id (integer, primary key)
- question (text)
- option_a (text)
- option_b (text)
- option_c (text)
- option_d (text)
- correct_answer (char) -> A/B/C/D
- category (text) -> huruf / angka / warna_bentuk
- difficulty (text) -> mudah / sedang / sulit
- created_at (timestamp)

### Tabel user_history
- id (integer, primary key)
- user_id (integer)
- question_id (integer)
- date (date)

## 4) Logika Pengambilan Soal Harian
1. Ambil semua soal yang valid kategori misi harian.
2. Buang soal yang sudah dikerjakan user pada tanggal hari ini.
3. Kelompokkan kandidat menjadi 3 prioritas:
   - Belum pernah dikerjakan user (prioritas tertinggi)
   - Pernah dikerjakan, tapi sudah lewat cooldown (prioritas menengah)
   - Pernah dikerjakan dalam periode dekat (prioritas terendah)
4. Pilih 2 soal secara acak dengan variasi kategori sebisa mungkin.
5. Setelah misi selesai, simpan daftar question_id ke user_history untuk tanggal hari itu.

## 5) Aturan Anti-Pengulangan
- Hard rule: tidak boleh mengulang soal yang sama pada hari yang sama untuk user yang sama.
- Soft rule: pengulangan soal lama diizinkan jika bank soal baru tidak cukup, dengan jeda cooldown.
- Contoh cooldown: 3 hari.

## 6) Rekomendasi Bank Soal
- Minimal 30 soal per kategori (huruf, angka, warna_bentuk).
- Distribusi tingkat kesulitan:
  - mudah: 50%
  - sedang: 35%
  - sulit: 15%
- Total awal yang disarankan: 90 soal.

## 7) Contoh Bentuk Soal
- Huruf: identifikasi huruf, urutan huruf, pasangan huruf besar-kecil, huruf vokal.
- Angka: identifikasi angka, urutan angka, sebelum/sesudah, nama bilangan ke simbol.
- Warna/Bentuk: identifikasi warna dasar, hasil campuran sederhana, ciri bangun ruang dasar.

## 8) Tujuan Sistem
- Menjaga variasi soal harian.
- Membantu pembelajaran huruf, angka, warna, dan bangun ruang.
- Mengurangi kebosanan dengan rotasi soal yang adil dan acak.
