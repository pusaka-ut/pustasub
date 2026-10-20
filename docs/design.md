# Design System & UI/UX Guidelines — PUSTASUB
**Official Style Name: "Soft Lilac CandyClay Studio" (Authentic Claymorphism & Neumorphism Fusion — Soft Lilac Canvas, Zero Neon, Zero Pure White, Dynamic Rounded Typography, Official Logo Integration)**

Dokumen ini adalah *Single Source of Truth* mutlak untuk pedoman estetika visual, tata warna, sistem komponen, tipografi dinamis, dan interaktivitas antarmuka PUSTASUB. Dilarang keras menggunakan warna putih murni (`#FFFFFF`), latar belakang biru gelap pada kanvas studio, efek pendaran neon glowing (`box-shadow: 0 0 Xpx`), atau entitas unicode jadul pada tombol.

---

## 1. Filosofi & Konsep Desain: "Soft Lilac CandyClay Studio"

Konsep desain PUSTASUB memadukan **Claymorphism** (bantalan 3D fisik empuk montok seperti permen/dessert candy, marshmallow cream, kurva membulat lembut, kilau glaze atas) dan **Neumorphism** (ceruk tenggelam *sunken insets* yang menyatu mulus dengan kanvas).
- **Kanvas Studio Soft Lilac / Muted Lavender (Amanah Khusus Bos):** Latar belakang antarmuka menggunakan warna ungu muda lembut / pastel keputihan (`#ECE8F6` / `#F0ECF8` / `#F4F0FA`). DILARANG menggunakan warna biru gelap sebagai background studio.
- **Kartu 3D Montok Marshmallow Cream (`#FAF7FE` / `#F5F1FB`):** Panel kontrol dan monitor siaran mengambang empuk di atas kanvas dengan bayangan ambient difusi natural, kilau glaze Vanilla Cream, dan bayangan bevel internal.
- **Universitas Terbuka Visual Identity:** Warna pahlawan kontrol adalah **Reflex Blue** (`#034694` / `#0E21A0`) dan **Honey Yellow** (`#FFDE00` / `#D48B00`), diselaraskan dengan pita warna ungu-violet (`#7C3AED`) dari logo resmi.
- **Integrasi Logo Resmi:** Menampilkan monogram soundwave 3D dari `docs/logo.png` dan logo teks `docs/logo_teks.png`.
- **Zero Clutter (Bebas Badge Murahan):** Tidak ada chip versi atau badge live dekoratif formalitas.
- **Icon Vektor SVG Profesional:** Seluruh aksi menggunakan icon vektor presisi (standar Lucide).
- **HUKUM MUTLAK ZERO-NEON & ZERO-GLOW:** DILARANG KERAS menggunakan efek glow neon (`box-shadow: 0 0 Xpx [color]`) atau radial gradient kabur.
- **Zero Pure White Rule (Mutlak):** DILARANG KERAS menggunakan `#FFFFFF` murni. Seluruh elemen highlight menggunakan **Vanilla Cream** (`#FFFDF0`), **Sweet Custard** (`#FFF8D6`), atau **Sweet Milk** (`#F0F4FC`).

---

## 2. Tipografi Dinamis "CandyClay" (Anti-Kaku)

Wajib menggunakan reset eksplisit `button, input, select, textarea, kbd { font-family: inherit; }`:
1. **Heading, Brand Title, Action Buttons & Numeric Metrics:**
   - **Font Utama:** **Outfit** (`weights: 600, 700, 800, 900`).
2. **Body Text, Labels, Deskripsi & Live Subtitle:**
   - **Font Pendamping:** **Plus Jakarta Sans** (`weights: 500, 600, 700`).

---

## 3. Palet Warna Resmi (Official Soft Lilac CandyClay Palette)

```
┌────────────────────────────────────────────────────────────────────────┐
│             PUSTASUB "SOFT LILAC CANDYCLAY" OFFICIAL COLOR SYSTEM      │
├────────────────────┬─────────────┬─────────────────────────────────────┤
│ Peran Warna        │ Kode Hex    │ Karakter & Penggunaan               │
├────────────────────┼─────────────┼─────────────────────────────────────┤
│ Canvas Soft Lilac  │ #ECE8F6     │ Ungu muda lembut kanvas studio      │
│ Canvas Lilac Light │ #F4F0FA     │ Variasi kanvas sekunder             │
│ Surface Marshmallow│ #FAF7FE     │ Bantalan kartu 3D empuk montok      │
│ Surface Elevated   │ #F5F1FB     │ Highlight elevasi kartu clay        │
│ Sunken Cavity      │ #DFD8E9     │ Ceruk inset track VU & input teks   │
├────────────────────┼─────────────┼─────────────────────────────────────┤
│ Primary Blue (UT)  │ #034694     │ R 3, G 70, B 148 (Reflex Blue UT)   │
│ Electric Indigo    │ #0E21A0     │ Biru siaran tombol master           │
│ Honey Yellow (UT)  │ #FFDE00     │ Kuning madu border & aksen          │
│ Honey Amber Accent │ #D48B00     │ Aksen teks madu kontras di bg terang│
│ Vivid Violet Ribbon│ #7C3AED     │ Selaras pita logo resmi             │
│ Panic Strawberry   │ #E11D48     │ Merah permen jelly tombol darurat   │
├────────────────────┼─────────────┼─────────────────────────────────────┤
│ Deep Navy Text     │ #0C1E4A     │ Teks Heading & Label Utama (AAA)    │
│ Muted Slate Text   │ #5A6A85     │ Teks sekunder, keterangan           │
│ Vanilla Cream Tint │ #FFFDF0     │ Pengganti PUTIH di tombol gelap     │
│ Sweet Custard Tint │ #FFF8D6     │ Teks subtitle monitor kontras       │
└────────────────────┴─────────────┴─────────────────────────────────────┘
```

---

## 4. Sistem Fisika Bayangan: 3-Shadow Recipe (Strictly Zero-Neon)

### A. Formula Kartu 3D Marshmallow Cream (`.candy-card`)
```css
.candy-card {
  background: #FAF7FE;
  border-radius: 28px;
  border: 1.5px solid rgba(124, 58, 237, 0.12);
  box-shadow: 
    10px 16px 36px -4px rgba(60, 40, 110, 0.15),
    inset 2.5px 2.5px 5px rgba(255, 253, 240, 0.9),
    inset -2.5px -2.5px 5px rgba(110, 95, 145, 0.12);
  position: relative;
}
```

### B. Ceruk Neumorphic Tenggelam (`.candy-input`, `.gummy-vu-track`)
```css
.candy-input, .gummy-vu-track {
  background: #DFD8E9;
  border: 1.5px solid rgba(140, 125, 175, 0.25);
  border-radius: 9999px;
  box-shadow: 
    inset 3px 3px 8px rgba(70, 50, 110, 0.22),
    inset -2px -2px 6px rgba(255, 253, 240, 0.65);
  color: #0C1E4A;
}
```

### C. Tombol Aksi Permen Kenyal (`.btn-candy-primary`, `.btn-panic-clear`)
```css
.btn-candy-primary {
  background: linear-gradient(135deg, #034694 0%, #0E21A0 100%);
  color: #FFDE00;
  font-family: "Outfit", sans-serif;
  font-weight: 800;
  border-radius: 9999px;
  border: none;
  box-shadow: 
    6px 10px 20px -3px rgba(3, 70, 148, 0.35),
    inset 2px 2px 4px rgba(255, 253, 240, 0.4),
    inset -2px -2px 4px rgba(2, 20, 60, 0.3);
  transition: all 160ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.btn-candy-primary:active {
  transform: scale(0.95);
  box-shadow: 
    2px 4px 10px -2px rgba(255, 222, 0, 0.25),
    inset 3px 3px 6px rgba(180, 130, 0, 0.5);
}
```

---

## 5. Komponen Kunci UT CandyClay Studio

### 1. Interactive Audio VU Meter (Sunken Gummy Bar)
- **Tampilan:** Kapsul membulat ceruk hitam pekat (`#071026`) dengan segmen-segmen empuk permen jelly.
- **Skema Warna Bebas Neon:**
  - Optimal (0% - 75%): Reflex Blue `#034694` $\to$ Electric Indigo `#0E21A0`
  - Warning (75% - 88%): Honey Yellow `#FFDE00`
  - Peak / Over (88% - 100%): Strawberry Jelly `#E11D48`
- **Zero-Neon Indicator:** Menggunakan jarum pin permen kuning solid dengan specular highlight, bukan laser glow.

### 2. Live Broadcast Switcher & Emergency Panic Cluster
- **Live Button:** Kapsul kuning madu montok bertekstur permen karet dengan dot status live.
- **Panic Clear Button:** Tombol merah permen jelly berdampingan dengan badge hotkey `[ESC]`. Saat ditekan, subtitle layar terhapus seketika (<15ms).
- **Hold / Freeze Switch:** Toggle kapsul es manis (*frost pill*) untuk menahan teks di layar saat pembicara berhenti sejenak.

### 3. Dedicated English Engine Badge
- Badge berbentuk pil permen empuk bertuliskan `ENGLISH ASR • UT ACCENT INTELLIGENCE` di header dashboard studio.

### 4. Kotak Terjemahan Fleksibel Mandiri (Floating Modular Card)
- Kotak mandiri bervolume clay empuk dengan badge pill Honey Yellow `TERJEMAHAN ID`, teks Sweet Custard, dan kontrol penempatan fleksibel (Kanan Bawah, Kanan Atas, Di Bawah Subtitle EN).

---

## 5. Tata Letak Terpusat Maksimal & Sistem Responsif Ergonomis

### A. Dimensi Kanvas Terpusat Mantap
- **Lebar Maksimal:** `max-width: min(1580px, 95vw)` dengan `margin: 0 auto;`.
- Kanvas membentang secara proporsional di resolusi Full HD (1920x1080), 2K, maupun 4K tanpa menyisakan ruang kosong timpang di tepi layar.
- **Skala Spasi 8pt Bernapas:**
  - Padding kartu: `clamp(20px, 2.2vw, 30px)`.
  - Gap kartu utama: `clamp(18px, 1.8vw, 24px)`.
  - Margin & padding internal: presisi dan rapi, tanpa elemen yang saling tumpang tindih (*anti-stacking*).

### B. Alokasi Ergonomi Area Fitur
- **Kendali Utama Siaran (~60% kolom kiri):** Strip komando ringkas, padat, dan taktis. Tombol aksi utama (Mulai/Hentikan Subtitle, Hapus Layar, Tahan Teks) proporsional dan tidak meregang liar.
- **Monitor Siaran Langsung (Centerpiece 16:9):** Area mahkota visual di kolom utama dengan aspect ratio 16:9 terkunci agar operator memiliki referensi visual siaran yang akurat.
- **Terjemahan Bahasa Indonesia:** Area baca horizontal nyaman dengan gelembung teks yang tidak sempit.
- **Kolom Kontrol Sekunder (~40% kolom kanan):** Didekonstruksi menjadi 3 kartu mandiri terpisah bernapas lega (`.device-card`, `.vocab-card`, `.styling-card`) agar fitur penting tidak berhimpitan.

### C. 4 Level Breakpoint Responsif
1. **Large Desktop (≥1440px):** 2-kolom terpusat megah (`1.5fr 1fr`), monitor 16:9 maksimal, spasi lapang.
2. **Standard Laptop (1024px – 1439px):** 2-kolom adaptif (`minmax(0, 1.35fr) minmax(360px, 1fr)`).
3. **Tablet (768px – 1023px):** 1-kolom terstruktur rapi, urutan prioritas visual tetap terjaga.
4. **Mobile (≤767px):** 1-kolom penuh, padding tepi 16px, tombol beralih vertikal dinamis tanpa clipping.

---

## 6. Dekonstruksi 3 Kartu Mandiri Kolom Kanan & Kamus Wording Humanis

### A. Dekonstruksi 3 Kartu Mandiri (Anti-Crowded)
1. **Sumber Suara (`.device-card`):**
   - Kartu mandiri ringkas berjarak lega.
   - Pilihan masukan suara dengan label elegan `Suara Komputer (Loopback Default)`.
2. **Kamus Istilah Khusus (`.vocab-card`):**
   - Menampung input istilah baru, seleksi kategori (Akademik, Pimpinan, Fakultas, Konferensi, Teknologi), tombol Simpan, dan badge counter total istilah.
   - Area chip penampung istilah fleksibel dan memiliki ruang bernapas.
3. **Gaya & Posisi Subtitle (`.styling-card`):**
   - Pilihan Tema siaran (Formal Akademik, Presentasi Slide, Minimalis Halus, Talkshow Hangat, Pita Berita, Balon Dialog, Banner Atas).
   - Posisi Subtitle (Bawah, Atas, Tengah, Sisi Kiri, Sisi Kanan).
   - Penyesuaian Visual: 4 slider presisi (Ukuran Teks, Kepekatan Latar, Lengkungan Sudut, Tebal Garis Tepi).

### B. Kamus Wording Humanis & Elegan (Bebas Jargon Teknis)
- `Master Broadcast Control` $\to$ **Kendali Utama Siaran**
- `START ENGINE` / `STOP ENGINE` $\to$ **Mulai Subtitle** / **Hentikan Subtitle**
- `PANIC CLEAR` $\to$ **Hapus Layar**
- `FREEZE` / `UNFREEZE` $\to$ **Tahan Teks** / **Lanjutkan Teks**
- `Audio Loopback Signal (WASAPI)` $\to$ **Indikator Suara Masuk**
- `Live Broadcast Monitor (16:9)` $\to$ **Monitor Siaran Langsung (16:9)**
- `Open Overlay` $\to$ **Buka Jendela Overlay**
- `ID TRANSLATION` $\to$ **TERJEMAHAN ID**
- `Indonesian Sentence Translation` $\to$ **Terjemahan Bahasa Indonesia**
- `Latest Sentence Translation (ID)` $\to$ **Kalimat Terjemahan Terakhir**
- `Floating Card Position` $\to$ **Posisi Kotak Terjemahan**
- `Bottom-Right`, `Top-Right`, `Below English` $\to$ **Kanan Bawah**, **Kanan Atas**, **Bawah Teks**
- `Audio Ingestion Mode & Device` $\to$ **Sumber Suara**
- `Universitas Terbuka Vocabulary (SQLite Indexed)` $\to$ **Kamus Istilah Khusus**
- `Broadcast Styling & Tuning` $\to$ **Gaya & Posisi Subtitle**
- `Preset Gaya Siaran` $\to$ **Pilihan Tema**
- `Posisi Layar` $\to$ **Posisi Subtitle**
- `Live Style Tuning` $\to$ **Penyesuaian Visual**

---

## 7. Blacklist Mutlak AI-Slop & Aturan Anti-Neon (Quality Gate)

Sebelum komponen antarmuka dinyatakan selesai:
- [ ] **ZERO NEON:** Tidak ada satu pun baris CSS yang menggunakan `box-shadow: 0 0 Xpx` (glowing neon).
- [ ] **ZERO PURE WHITE:** Tidak ada penggunaan kode warna `#FFFFFF` pure di seluruh elemen UI (wajib Vanilla Cream `#FFFDF0`).
- [ ] **DYNAMIC TYPOGRAPHY:** Font heading, brand, tombol, dan metrik menggunakan **Outfit**; teks body menggunakan **Plus Jakarta Sans**.
- [ ] **TACTILE CLAY RECIPE:** Setiap kartu menerapkan 3 lapisan bayangan fisik (outer ambient + inner highlight + inner depth).
- [ ] **SUNKEN INSET:** Input dan track indikator mengadopsi ceruk tenggelam empuk (`#071026`).
- [ ] **KONTROL AKTIF DUA ARAH:** Seluruh tombol, switch, dan slider terhubung fungsional dua arah dengan backend.
