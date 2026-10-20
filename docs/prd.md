# PRODUCT REQUIREMENT DOCUMENT (PRD)

## Project: PUSTASUB (Live Subtitle Engine for OBS & vMix)
**Product Brand:** PUSTASUB (PustaSub AI)  
**Philosophy:** Mengabadikan tuturan lisan webinar akademik menjadi pustaka teks siaran secara real-time.  
**Version:** 1.1.0 (Final Approved & Refined Specification)  
**Target Environment:** Windows 10/11 (Local Offline Deployment)  
**Author:** AI System Architect & Senior Broadcast Software Engineer  
**Status:** Approved for Final Architecture & Development  

---

## 1. Executive Summary & Product Vision

**PUSTASUB (PustaSub AI)** adalah engine desktop mandiri yang berjalan 100% offline di laptop/PC streaming lokal untuk menghasilkan subtitle secara real-time (*verbatim speech-to-text*) dengan latensi sub-detik (<300ms).

Engine ini dirancang khusus untuk operator broadcast webinar internasional, siaran akademik, dan live event yang menggunakan **OBS Studio** atau **vMix** untuk siaran langsung ke YouTube Live dan platform streaming lainnya.

### Visi Utama:
- **Zero Cloud & Zero Latency:** Tidak memerlukan koneksi internet, tidak ada biaya API token per jam, kebal terhadap gangguan jaringan internet.
- **Ultra-Lightweight on Streaming Hardware:** Mengonsumsi resource CPU/VRAM sangat rendah (CPU <8%, RAM <200MB) sehingga laptop streaming tetap lancar melakukan encoding video 1080p60 tanpa *dropped frames*.
- **Universal Audio Ingestion & Selective Process Capture:** Menangkap audio sistem via Windows WASAPI Loopback murni (Master Default) serta mendukung *Process-Specific Loopback* (hanya merekam audio proses Zoom/Teams/Chrome tanpa gangguan notifikasi Windows).
- **Dual Broadcast Compatibility:** Mendukung integrasi *Browser Source* (OBS & vMix) melalui WebSocket kecepatan tinggi dan *Text Source File* atomik untuk vMix Title Data Source.
- **Mission-Critical Broadcast Safeguard:** Dilengkapi tombol darurat *Panic Clear (Censor)*, *Hold/Freeze*, hotkey keyboard, dan auto-failover saat perangkat audio USB/headset terlepas.
- **1-Click Portable Distribution:** Aplikasi dapat didistribusikan ke berbagai laptop operator dengan konsep *zero-install* (tinggal klik langsung jalan tanpa instalasi Python).
- **CandyGlaze Soft-UI Design System:** Tampilan kontrol operator yang modern, manis, bertekstur empuk permen timbul (*Sweet Claymorphism*), menggunakan warna identitas resmi PANTONE Reflex Blue C + PANTONE 109 C Yellow + Violet, tanpa warna putih murni.

---

## 2. Problem Statement & User Personas

### Problem Statement
1. **Ketiadaan Subtitle Real-Time di YouTube Live:** YouTube Live tidak menyediakan subtitle instan otomatis untuk penonton di banyak jenis perangkat siaran langsung.
2. **Audio Routing yang Rumit & Kebocoran Suara:** Sebagian besar software subtitle mengharuskan instalasi driver *Virtual Audio Cable* pihak ketiga, dan sering kali suara denting notifikasi Windows ikut masuk ke dalam teks siaran.
3. **Komputasi Rakus Resource:** Model AI seperti OpenAI Whisper standar memakan komputasi GPU/CPU yang sangat besar (CPU 25-50%, VRAM >1.5GB), memicu *overheating* dan *drop frames* pada laptop yang sedang encoding OBS/vMix.
4. **Kelelahan Visual Membaca Subtitle:** Subtitle yang berganti terlalu cepat kata-per-kata per milidetik membuat mata penonton lelah. Dibutuhkan mode pacing kalimat yang nyaman dibaca penonton siaran TV.
5. **Insiden di Siaran Langsung:** Tidak adanya tombol darurat untuk menghapus teks seketika saat pembicara salah ucap atau batuk.

### Target User Persona
- **Broadcast Operator / System Engineer:** Mengoperasikan OBS atau vMix pada siaran webinar berdurasi 2 hingga 8 jam. Membutuhkan stabilitas mutlak, VU meter visual permen 30 fps, tombol Panic Clear cepat, dan pergantian preset 1-klik.
- **Presenter & Event Organizer:** Membutuhkan teks subtitle yang bersih, jelas dibaca audiens internasional, serta mampu mengenali istilah ilmiah atau nama pembicara secara akurat.

---

## 3. Goals & Success Metrics

### Key Goals
- **Latensi Sub-Detik:** Kata yang diucapkan pembicara muncul di layar dalam waktu 150ms – 300ms.
- **Akurasi Tinggi untuk Bahasa Inggris & Bilingual Ready:** Word Error Rate (WER) rendah dengan dukungan arsitektur Language Gate (English Zipformer default + Indonesian Zipformer switcher).
- **Zero-Driver Requirement & Process Isolation:** Mampu merekam suara Zoom/Browser tanpa driver virtual, serta opsi isolasi proses aplikasi.
- **Zero Memory Leak & Auto-Failover:** Mampu berjalan nonstop selama lebih dari 12 jam dengan konsumsi RAM stabil < 200MB, dan auto-reconnect dalam <1.5 detik jika headset terlepas.
- **Zero-Dependency Distribution:** Paket rilis aplikasi dapat langsung dijalankan dengan 1-klik di Windows 10/11 tanpa menginstall Python terlebih dahulu.

### Success Metrics (KPI)
| Metrik | Target |
|---|---|
| Latensi End-to-End | < 300 ms |
| Penggunaan CPU (Intel i5/i7 / Ryzen 5/7) | < 8% (kondisi transkripsi aktif) |
| Penggunaan RAM | < 200 MB konstan |
| Drop Frame OBS/vMix | 0% (tidak berdampak pada encoding siaran) |
| Latensi Panic Clear (Tombol Darurat) | < 15 ms hingga layar OBS bersih |
| Failover Reconnect Audio | < 1.5 detik saat device fisik dicabut |
| Startup Time Aplikasi | < 2 detik hingga dashboard siap |

---

## 4. Input Audio Specification & Resilience Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AUDIO INGESTION MATRIX                          │
├────────────────────────┬─────────────────────┬─────────────────────────┤
│ Kategori Sumber Suara  │ Contoh Sumber Suara │ Jalur Penangkapan       │
├────────────────────────┼─────────────────────┼─────────────────────────┤
│ Mode Loopback Master   │ - Semua audio sistem│ Windows WASAPI          │
│ (Default Ingestion)    │ - Zoom, Web, VLC    │ Loopback Capture        │
├────────────────────────┼─────────────────────┼─────────────────────────┤
│ Mode Selective Process │ - Khusus Zoom.exe   │ Windows CoreAudio       │
│ (Anti-Notifikasi Win)  │ - Khusus Chrome.exe │ Process-Loopback Capture│
│                        │ - Khusus Teams.exe  │ (Isolasi suara aplikasi)│
├────────────────────────┼─────────────────────┼─────────────────────────┤
│ Mode Physical Input    │ - Capture Card HDMI │ DirectShow / WASAPI     │
│ (Input perangkat luar) │ - Kamera USB / Mic  │ Physical Device Capture │
└────────────────────────┴─────────────────────┴─────────────────────────┘
```

### Arsitektur Ketahanan Audio:
1. **WASAPI Silence Feeder (Anti-Starvation):** Injeksi silent frames (0 PCM) 16 kHz jika tidak ada buffer masuk dalam >40ms saat pembicara hening, menjaga clock internal streaming ASR tetap stabil.
2. **High-Performance Resampling (C-Binding):** Konversi stereo ke mono dan resampling 44.1k/48k ke 16k dilakukan secara *zero-copy chunk-based* di memori.
3. **Dynamic Hardware Audio Failover:** Listener background yang memantau perubahan status endpoint Windows. Jika headset dicabut, engine otomatis menyambung ke default device baru tanpa crash.

---

## 5. System Architecture & Technical Specifications

```
  ┌────────────────────────────────────────────────────────┐
  │                 AUDIO INGESTION LAYER                  │
  │   WASAPI Loopback (Master / Process-Specific) OR Mic   │
  │     Resampling C-Binding & Silence Feeder (16kHz PCM)  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │           ASR & NLP CORE WITH LANGUAGE GATE            │
  │ ├─ Language Gate Switcher (English Zipformer / Indo)   │
  │ ├─ Streaming Zipformer ASR (sherpa-onnx C++ Runtime)   │
  │ ├─ Silero VAD (Voice Activity Detection)               │
  │ ├─ Hotwords Boosting (Kustom istilah & nama pembicara) │
  │ ├─ Dual Pacing Formatter (Word Flow vs Paced Chunk)    │
  │ └─ Hybrid Fast Punctuation & Sentence Formatter        │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │               BROADCAST DELIVERY SERVICE               │
  │ ├─ High-Speed WebSocket Server (port 8765)             │
  │ ├─ Local HTTP Web Server (Control Panel & Overlay)     │
  │ ├─ Panic / Censor Event Dispatcher (<15ms wipe)        │
  │ ├─ Atomic File Writer (`current_subtitle.txt` for vMix)│
  │ └─ Session Transcript Recorder (.srt & .txt)           │
  └───────────────────────────┬────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌──────────────────┐                     ┌──────────────────┐
│    OBS STUDIO    │                     │       vMIX       │
│  Browser Source  │                     │  Browser Input   │
│  (WebSocket Live)│                     │  OR Data Source  │
└──────────────────┘                     └──────────────────┘
```

### Core Technologies:
1. **Core Runtime:** Python 3.10+ (Embedded Distribution untuk deployment mandiri).
2. **Streaming ASR Engine:** `sherpa-onnx` (Streaming Zipformer teroptimasi ONNX Runtime C++).
3. **Audio Capture Engine:** `PyAudioWPatch` + Windows Process Loopback filter.
4. **Local Web Server & WebSocket:** `FastAPI` / `Uvicorn` + WebSockets.
5. **Frontend Dashboard & Overlay:** Vanilla HTML5, CandyGlaze CSS (Sweet Claymorphism), Zero-dependency Vanilla JS.
6. **Distribution & Packaging:** Windows Self-Contained Portable Suite + Inno Setup Wizard Installer.

---

## 6. Functional Requirements (Fitur & Fungsionalitas)

### FR-1: Audio Device Management & Process Isolation
- **FR-1.1:** Deteksi otomatis seluruh perangkat output suara sistem untuk mode *Master Loopback*.
- **FR-1.2:** Deteksi proses audio aktif (Zoom, Chrome, Teams) untuk mode *Process-Specific Loopback* guna mengisolasi suara aplikasi dari notifikasi sistem.
- **FR-1.3:** Auto-failover hardware audio: otomatis reconnect dalam <1.5 detik saat kabel audio dicabut.
- **FR-1.4:** VU Meter visual interaktif permen 30 fps di dashboard.

### FR-2: Real-Time Speech Recognition & Language Gate
- **FR-2.1:** Transkripsi bahasa Inggris langsung tanpa jeda (latensi sub-detik <300ms).
- **FR-2.2 (Language Gate):** Arsitektur multi-model switcher di dashboard yang memungkinkan operator beralih antara Model Bahasa Inggris (Default) dan Model Bahasa Indonesia tanpa restart engine.
- **FR-2.3:** Finalisasi frasa dengan kapitalisasi awal kalimat dan tanda baca otomatis menggunakan jeda VAD.

### FR-3: Dual Pacing Modes (Ergonomi Tampilan Audiens)
- **FR-3.1 (Live Rolling Word Flow):** Kata muncul satu demi satu secara inkremental (*karaoke/teleprompter style*).
- **FR-3.2 (Broadcast Paced Chunk):** Kata ditampung dalam buffer mikro 3-5 kata dan ditampilkan per frasa utuh dengan transisi halus (*TV broadcast style*).
- **FR-3.3:** Toggle pemilihan mode pacing di dashboard kontrol operator.

### FR-4: Mission-Critical Safeguard (Kontrol Darurat Operator)
- **FR-4.1 (Panic Clear / Censor):** Tombol darurat di header dashboard dan hotkey keyboard (`Esc` atau `Ctrl+Space`) yang langsung mengosongkan subtitle di OBS dan vMix dalam waktu <15ms.
- **FR-4.2 (Hold / Freeze Subtitle):** Tombol untuk membekukan subtitle aktif di layar agar tidak memudar saat pembicara berhenti sejenak.

### FR-5: Hotwords / Vocabulary Boosting
- **FR-5.1:** Input teks di dashboard untuk memasukkan daftar kata kunci khusus (contoh: *"Universitas Terbuka", "Chancellor", "Pedagogy"*).
- **FR-5.2:** Peningkatan bobot probabilitas model agar ejaan kata teknis dan nama orang selalu tepat.

### FR-6: 1-Click Profile Presets & Styling Customizer
- **FR-6.1 (Profile Presets):** Tombol preset 1-klik di dashboard:
  - *"Academic Formal"* (Teks besar, kontras tinggi, lower-third)
  - *"Slide-Friendly"* (Subtitle 1 baris ramping di batas bawah layar)
  - *"Minimalist Glass"* (Transparansi tinggi tanpa background tebal)
- **FR-6.2 (Custom Visual Tuning):** Slider font size (24px - 72px), warna teks (Vanilla Cream), outline, dan background opacity.
- **FR-6.3:** Live preview 16:9 yang menampilkan subtitle persis seperti di OBS/vMix secara real-time.

### FR-7: Dual Output untuk OBS & vMix
- **FR-7.1 (Browser Source):** URL `http://127.0.0.1:8765/overlay` untuk OBS/vMix Browser Source.
- **FR-7.2 (Text Source File):** File `output/current_subtitle.txt` yang diperbarui secara atomik untuk vMix Title XAML.
- **FR-7.3 (Session SRT Logging):** Penyimpanan transkrip lengkap selama siaran ke dalam format `.srt` dan `.txt` bertanda waktu.

### FR-8: 10x Smarter ASR & Broken English Intelligence Core
- **FR-8.1 (High-Capacity Zipformer & Beam Search):** Dukungan model berkapasitas lebih tinggi (`sherpa-onnx-streaming-zipformer-en-2023-06-26`) dengan decoding *Modified Beam Search* (beam size 4) untuk mengenali ucapan beraksen tebal.
- **FR-8.2 (Indonesian-Accent Phonetic Normalizer):** Modul pemetaan fonetik otomatis untuk pelafalan khas Indonesia pada istilah akademik dan teknis bahasa Inggris ("unipersiti", "rek-tor", "pjj", "diskusi", "aktip").
- **FR-8.3 (Disfluency Culler & Grammar Repair):** Pembersihan kata pengisi lisan ("um", "uh", "you know", "anu") dan rekonstruksi tata bahasa broken English secara real-time (<5ms) menjadi kalimat siaran yang rapi.
- **FR-8.4 (Contextual Memory Buffer):** Penyimpanan buffer 3 kalimat terakhir untuk mendisambiguasi homofon berdasarkan topik seminar.

### FR-9: Ultra-Flexible Multi-Zone Presentation Suite
- **FR-9.1 (Multi-Zone Positioning):** Penempatan subtitle fleksibel pada kanvas 1080p: Lower-Third (Bottom), Top-Banner (Top), Center-Box, Side-Pill, dan Custom Free-Drag X/Y Offset (0% - 100%).
- **FR-9.2 (8 Rich Aesthetic Presets):** Ekspansi gaya visual siaran: Academic Formal, Slide-Friendly Slim, Minimalist Glass, Talkshow Honey, Glow Neon Candy, News Ticker Ribbon, Speech Bubble Playful, Top-Banner Clean.
- **FR-9.3 (Dynamic Karaoke Word Glow):** Kata yang sedang aktif diucapkan bersinar dengan Honey Yellow Glow sebelum menyatu ke warna Vanilla Cream.
- **FR-9.4 (Speaker Badge Injection):** Penanda pill nama dan gelar pembicara yang dapat diaktifkan/dinonaktifkan langsung dari dashboard.
- **FR-9.5 (Custom Preset Creator):** Operator dapat menyimpan racikan gaya dan posisi subtitle ke dalam preset baru yang tersimpan permanen di `config.json`.

---

## 7. Packaging & Multi-Device Distribution Architecture

- **Format Portable:** `PUSTASUB-v1.1.0-Portable.zip` (Tinggal ekstrak dan jalankan `PUSTASUB.exe`).
- **Format Installer:** `PUSTASUB-v1.1.0-Setup.exe` (Inno Setup wizard dengan shortcut desktop).
- **Zero Python Dependency:** Memanfaatkan Python 3.10+ Embedded Distribution resmi + ONNX Runtime DLL pre-compiled + model pre-bundled. Bebas false-positive Windows Defender.

---

## 8. UI/UX Design System: "CandyGlaze Soft-UI"

- **Konsep:** Sweet Claymorphism / Soft Neumorphism bertema makanan manis & permen timbul.
- **Palet Warna Baku:**
  - PANTONE Reflex Blue C: `#034694`
  - PANTONE 109 C Yellow: `#FFDE00`
  - Violet Palette: `#4D2FB2`, `#0E21A0`, `#B153D7`, `#9929EA`
- **Zero Pure White Rule:** Pengganti putih murni adalah **Vanilla Cream (`#FFFDF0`)** dan **Sweet Milk (`#F8F6FE`)**. Latar canvas menggunakan **Marshmallow Base (`#F3F0FA`)**.
- **Progressive Disclosure:** Tampilan utama tetap bersih (hanya tombol Live Switcher, VU Meter, Panic Clear, dan Copy Link), sementara kontrol detail (slider style, hotwords, audio process selector) tersusun dalam accordion empuk yang rapi.
