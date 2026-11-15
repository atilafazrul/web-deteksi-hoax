# HoaxLens ID - Deteksi Hoaks Berita Indonesia (Vue.js 3 + Laravel + MySQL)

Aplikasi deteksi hoaks berita Indonesia dengan arsitektur terpisah **Frontend (Vue.js 3 Vite)** dan **Backend (Laravel + MySQL)**, terhubung ke mesin Machine Learning **TF-IDF + Calibrated Linear SVM (Akurasi 97.8%)**.

---

## Struktur Folder

```text
web-deteksi hoax/
├── backend/                  <-- Backend Laravel (Port 8000)
│   ├── app/
│   │   ├── Http/Controllers/ArticleController.php
│   │   └── Models/Article.php, ArticleSentence.php
│   ├── config/cors.php
│   ├── database/migrations/  <-- Skema MySQL (articles, article_sentences)
│   ├── routes/api.php        <-- Endpoint REST API
│   └── .env                  <-- Konfigurasi DB MySQL
├── frontend/                 <-- Frontend Vue.js 3 Vite (Port 5173)
│   ├── src/
│   │   ├── App.vue           <-- Komponen Reaktif Utama Vue 3
│   │   └── main.js
│   ├── vite.config.js        <-- Proxy ke http://127.0.0.1:8000
│   └── package.json
├── saved_models/             <-- Bobot Model ML (svm_tfidf_pipeline.joblib)
├── src/                      <-- Modul ML & Scraper Berita (Kompas, Detik, CNN, dll.)
├── run_analysis.py           <-- Jembatan CLI Python antara Laravel & Model ML
├── run_backend.bat           <-- Shortcut jalanin Laravel
├── run_frontend.bat          <-- Shortcut jalanin Vue 3
└── run_all.bat               <-- Shortcut jalanin keduanya sekaligus
```

---

## Cara Menjalankan Aplikasi

Pastikan layanan **MySQL** Anda sudah menyala (misal lewat **XAMPP** atau **Laragon** di port 3306).

### 1. Jalankan Backend (Laravel)
Buka terminal baru di folder proyek, lalu ketik:
```bash
cd backend
php artisan serve
```
> Backend berjalan di: `http://127.0.0.1:8000`

### 2. Jalankan Frontend (Vue.js 3 Vite)
Buka terminal kedua di folder proyek, lalu ketik:
```bash
cd frontend
npm run dev
```
> Frontend berjalan di: `http://localhost:5173`

*(Atau di Windows cukup klik 2x file `run_all.bat` untuk menjalankan keduanya secara otomatis).*

---

## Fitur Utama

1. **Deteksi dari Link Berita (URL Reader & Scraper)**:
   - Tempel link berita online dari Kompas, Detik, CNN Indonesia, Liputan6, Tempo, Antara, Merdeka, TurnBackHoax, dll.
   - Otomatis mengekstrak judul, tanggal, penulis, gambar, dan paragraf artikel.

2. **Deteksi Naskah Berita Manual**:
   - Salin dan tempelkan teks berita apa saja.

3. **Sorotan Kalimat Berisiko (*Sentence-Level Highlighting*)**:
   - Kalimat diwarnai berdasarkan skor hoaks:
     - 🔴 **Merah (>70%)**: Indikasi kuat hoaks / klaim manipulatif.
     - 🟡 **Kuning (45% - 70%)**: Mencurigakan / perlu cek fakta.
     - 🟢 **Hijau (<45%)**: Aman / bernada faktual resmi.
   - Klik kalimat mana pun untuk memeriksa persentase dan kata pemicu hoaksnya secara interaktif.

4. **Database MySQL Terintegrasi**:
   - Setiap berita yang diperiksa tersimpan otomatis ke tabel `articles` dan `article_sentences`.
   - Dilengkapi tab **"Riwayat MySQL"** untuk memuat ulang detail sorotan kalimat atau menghapus riwayat.
   - Tab **"Statistik DB"** untuk memantau total pemeriksaan dan domain media yang paling sering dicek.

5. **Penalaran Investigatif AI (Gemini Fact-Checking)**:
   - Memberikan argumentasi cek fakta berbasis jurnalisme investigatif.

6. **Ekspor & Berbagi**:
   - Salin ringkasan siap kirim ke WhatsApp.
   - Cetak atau simpan laporan sebagai PDF.
