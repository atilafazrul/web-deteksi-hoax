# HoaxLens ID - Chrome Extension (Manifest V3)

Ekstensi Google Chrome resmi untuk **HoaxLens ID** — Deteksi Hoaks Berita Indonesia secara instan langsung dari peramban (browser) Anda.

---

## Fitur Utama

1. **Analisis Halaman Aktif (URL Scanner)**:
   - Cukup buka artikel berita di portal mana pun (Kompas, Detik, CNN Indonesia, Liputan6, dll.), klik ikon ekstensi, lalu klik **"Analisis Berita di Halaman Ini"**.
   - Otomatis mengekstrak judul, metadata, persentase keyakinan hoaks, dan sorotan kalimat berisiko (*sentence-level highlighting*).

2. **Analisis Teks Manual**:
   - Tab khusus untuk menempelkan kutipan pesan berantai WhatsApp atau paragraf berita apa saja secara instan.

3. **Cek Teks Pilihan Cepat (*Right-Click Context Menu*)**:
   - Blok teks mencurigakan di halaman web mana pun -> Klik Kanan -> Pilih **"🔍 Periksa Hoaks dengan HoaxLens ID"**.
   - Notifikasi Chrome akan langsung muncul mengabarkan apakah teks tersebut terindikasi Hoaks atau Fakta beserta persentasenya.

4. **Indikator Status Backend & Pengaturan**:
   - Badge status di header (Hijau = Backend Aktif, Merah = Offline).
   - Opsi untuk mengubah base URL API backend (default: `http://127.0.0.1:8000`).

---

## Cara Memasang Ekstensi di Google Chrome

1. **Pastikan Backend Laravel Berjalan**:
   Buka terminal di root proyek dan jalankan:
   ```bash
   cd backend
   php artisan serve
   ```
   *(Backend berjalan di `http://127.0.0.1:8000`)*

2. **Buka Halaman Ekstensi di Chrome**:
   - Buka Google Chrome.
   - Ketik di URL bar: `chrome://extensions/` lalu tekan **Enter**.

3. **Aktifkan Developer Mode**:
   - Di pojok kanan atas, aktifkan sakelar **"Developer mode"** (Mode pengembang).

4. **Muat Ekstensi**:
   - Klik tombol **"Load unpacked"** (Muat yang belum dikemas) di pojok kiri atas.
   - Pilih folder:
     `d:\UMN\Semester 7\Deep Learning\web-deteksi-hoax\chrome-extensions`
   - Klik **Select Folder**.

5. **Selesai!**:
   - Ikon **HoaxLens ID** akan muncul di daftar ekstensi Chrome.
   - Pin ekstensi ke toolbar browser agar mudah diakses saat membaca berita.
