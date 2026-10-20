# PUSTASUB — Broadcast Subtitle & Live Translation Engine
### Universitas Terbuka (Pusat Perpustakaan & Layanan Terbuka)

PUSTASUB adalah sistem closed-captioning dan terjemahan langsung (live translation) berstandar siaran profesional (*broadcast-grade*) yang dirancang khusus untuk live streaming seremoni, wisuda, kuliah umum, dan webinar resmi Universitas Terbuka.

Sistem ini mendukung integrasi multi-software siaran seperti **OBS Studio**, **vMix**, dan **Wirecast** dengan latensi ultra-rendah dan akurasi tinggi.

---

## Fitur Utama

- **100% Standalone Portable (Zero-Dependency):** Tidak membutuhkan instalasi Python, Git, pip, atau compiler C di laptop target. Cukup ekstrak dan klik 1x untuk menjalankan.
- **ASR Latensi Rendah (Sherpa-ONNX Zipformer):** Pengenalan suara bahasa Inggris real-time berbasis streaming ONNX model tanpa ketergantungan koneksi internet.
- **Hybrid Live Translation (English to Indonesian):** Terjemahan real-time berbasis Neural Translation dengan fallback otomatis ke kamus glosarium akademik internal Universitas Terbuka saat offline.
- **Dual Broadcast Output:**
  - **OBS Studio:** Antarmuka web transparan dinamis via WebSocket (*Browser Source*) lengkap dengan 9 preset visual, karaoke glow, dan badge rektor/pembicara.
  - **vMix:** Ekspor atomik berkelanjutan ke berkas teks lokal (`output/current_subtitle.txt` dan `output/current_translation.txt`) untuk *vMix Title / Data Source*.
- **Admin Control Panel:** Panel kendali responsif untuk operator siaran (pemilihan mikrofon/loopback WASAPI, pemilihan preset tampilan, kontrol panic clear, freeze, dan live session logger).
- **1-Click OTA Auto-Updater:** Mekanisme pembaruan instan antar-perangkat via script `update.bat` tanpa perlu mengunduh ulang model AI berukuran besar.

---

## Panduan Penggunaan Cepat (Untuk Laptop Siaran)

Aplikasi telah dikemas dalam bentuk portabel pada berkas `PUSTASUB-v1.1.0-Portable.zip`.

### 1. Menjalankan Aplikasi
1. Ekstrak berkas `PUSTASUB-v1.1.0-Portable.zip` ke folder yang diinginkan di laptop siaran (misalnya `C:\PUSTASUB`).
2. Klik 2x pada berkas **`run.bat`** (atau **`PUSTASUB.vbs`** untuk mode hening di latar belakang).
3. Browser akan otomatis membuka panel kontrol operator pada alamat:
   ```
   http://127.0.0.1:8765/admin
   ```
4. Pada panel admin, pilih perangkat input audio (misal: *Microphone* atau *WASAPI Loopback* dari soundcard mixer).
5. Klik tombol **MULAI TRANSSKRIPSI** untuk memulai pengenalan suara siaran.

---

## Integrasi Broadcast Software

### A. Integrasi OBS Studio (Overlay Grafis)
1. Buka OBS Studio, tambahkan sumber baru (**Add Source**) bertipe **Browser**.
2. Berikan nama, misalnya `PUSTASUB Subtitle`.
3. Atur parameter Browser Source sebagai berikut:
   - **URL:** `http://127.0.0.1:8765/overlay`
   - **Width:** `1920`
   - **Height:** `1080`
   - Centang opsi **Shutdown source when not visible** dan **Refresh browser when scene becomes active**.
4. Subtitle dan terjemahan dwibahasa (*bilingual*) akan langsung muncul di kanvas siaran dengan styling animasi yang dipilih dari Admin Panel.

### B. Integrasi vMix (Lower-Third Title & Ticker)
1. Buka vMix, klik **Add Input** -> pilih **Title / XAML**.
2. Pilih template lower-third atau ticker yang diinginkan.
3. Klik kanan pada Title input di vMix -> pilih **Title Editor** -> klik tombol **Data Sources**.
4. Hubungkan Data Source ke berkas teks output lokal PUSTASUB:
   - **Teks Bahasa Asli:** `C:\PUSTASUB\output\current_subtitle.txt`
   - **Teks Terjemahan Indonesia:** `C:\PUSTASUB\output\current_translation.txt`
5. Atur pembaruan file menjadi otomatis (*auto-refresh on change*).

---

## Pembaruan Instan Antar-Device (1-Click OTA Update)

Ketika tim teknis merilis fitur atau perbaikan baru di repository pusat GitHub:
1. Pastikan laptop terhubung ke jaringan internet.
2. Tutup aplikasi PUSTASUB jika sedang aktif.
3. Klik 2x pada berkas **`update.bat`**.
4. Script akan mengunduh dan menyinkronkan berkas antarmuka dan modul logika terbaru dalam hitungan detik tanpa merusak model AI dan data lokal.

---

## Struktur Berkas Direktori

```
PUSTASUB/
├── pustasub-engine.exe    # Binary executable utama (Standalone native)
├── _internal/             # Runtime libraries & C-extensions
├── web/
│   ├── admin/             # Antarmuka Dashboard Operator Siaran
│   └── overlay/           # Antarmuka Grafis OBS Browser Source
├── models/                # Model Neural Sherpa-ONNX Offline
├── data/                  # Basis data SQLite & Glosarium Istilah Akademik UT
├── config/                # Berkas konfigurasi hotwords & kosakata
├── output/                # Berkas teks real-time vMix & sesi rekaman SRT
├── run.bat                # Peluncur utama dengan pembersihan port otomatis
├── PUSTASUB.vbs           # Peluncur mode hening latar belakang
└── update.bat             # Pembaruan instan 1-klik via GitHub
```

---

## Panduan Pengembang (Developer Mode)

Bagi pengembang yang ingin menjalankan langsung dari *source code* Python:

```bash
# 1. Kloning repositori
git clone https://github.com/pusaka-ut/pustasub.git
cd pustasub

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Jalankan server engine
python run.bat
```

Untuk mengemas ulang paket distribusi standalone:
```bash
python build/bundle_runtime.py
```

---

## Hak Cipta & Lisensi
Dikembangkan untuk Universitas Terbuka. Seluruh hak cipta dilindungi.
