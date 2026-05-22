# 🎭 Gaynonimous Chat Bot

> **Bot Telegram anonymous chat 1-lawan-1** dengan sistem keamanan media approval, peringatan scam bawaan, dan siap deploy ke Railway.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21.x-blue)](https://github.com/python-telegram-bot/python-telegram-bot)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)](https://sqlalchemy.org)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet?logo=railway)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🤔 Apa itu Gaynonimous Chat Bot?

Gaynonimous adalah bot Telegram yang menghubungkan dua pengguna secara **acak dan anonim** untuk saling bertukar pesan. Tidak ada yang tahu siapa lawan bicara mereka — tidak ada nama, tidak ada username, tidak ada nomor.

Bot ini dirancang dengan **keamanan sebagai prioritas utama**:
- Peringatan anti-scam muncul sejak `/start`
- Foto dan video **tidak bisa langsung dikirim** — harus disetujui penerima lebih dulu
- Sistem report dan blokir terintegrasi
- Admin dapat memantau dan mengelola seluruh aktivitas bot

---

## ✨ Fitur Lengkap

### 💬 Chat Anonim
- Matchmaking otomatis — pengguna yang masuk antrian akan dipasangkan secara acak
- Chat 1-lawan-1 tanpa saling mengetahui identitas
- Pesan teks, stiker, dan voice note langsung diteruskan ke lawan bicara
- Tombol **Next Partner** untuk ganti pasangan tanpa harus stop dulu
- Tombol **Stop Chat** untuk mengakhiri obrolan kapan saja

### 🛡️ Sistem Keamanan Media
Foto, video, animasi, dan dokumen **tidak langsung diteruskan**. Alurnya:

```
User A kirim foto
    ↓
Bot simpan file_id (tidak dikirim langsung)
    ↓
Bot tanya User B: "Lawan bicara ingin kirim media. Mau lihat?"
    + tombol [✅ Lihat Media]  [❌ Tolak]
    ↓
User B klik ✅  →  foto dikirim + User A diberi tahu "diterima"
User B klik ❌  →  foto tidak dikirim + User A diberi tahu "ditolak"
Tidak ada respons 60 detik → media expired, kedua pihak diberi tahu
```

### ⚠️ Peringatan Keamanan Bawaan
Setiap kali user mengetik `/start` dan membuka menu **Bantuan**, bot menampilkan peringatan:
- Jangan kirim uang ke orang asing
- Jangan bagikan nomor telepon, alamat, atau akun lain
- Jangan klik link mencurigakan
- Segera stop dan report jika ada pelecehan atau scam

### 🚩 Report & Blokir
- Tombol **Report User** tersedia langsung di keyboard chat
- Melaporkan otomatis memblokir partner tersebut dari muncul lagi di antrian kamu
- Laporan tersimpan di database dan bisa ditinjau admin

### 👤 Profil Anonim
- Menampilkan ID acak (bukan Telegram ID asli)
- Total jumlah obrolan yang pernah dilakukan
- Tanggal bergabung

### 🔧 Admin Panel
Semua perintah admin hanya bisa diakses oleh ID yang terdaftar di `ADMIN_IDS`.

| Perintah | Fungsi |
|---|---|
| `/admin_stats` | Statistik real-time: total user, antrian, chat aktif, pending media, laporan |
| `/admin_ban <user_id> [alasan]` | Ban user + putus chat aktif + notifikasi ke user |
| `/admin_unban <user_id>` | Unban user + notifikasi ke user |
| `/admin_broadcast <pesan>` | Kirim pesan ke semua user yang tidak dibanned |
| `/admin_reports` | Tampilkan 10 laporan terbaru beserta status tinjauan |

---

## 📱 Tampilan Keyboard

Bot menggunakan **ReplyKeyboardMarkup** — semua interaksi lewat tombol, bukan slash command.

### Menu Utama *(tidak sedang chat)*
```
┌─────────────────────┐
│    🔍 Cari Partner   │
├──────────┬──────────┤
│ 👤 Profil │ ❓ Bantuan│
└──────────┴──────────┘
```

### Mode Chat *(sedang obrolan)*
```
┌──────────────┬──────────┐
│ ⏭ Next Partner│ 🛑 Stop  │
├──────────────┴──────────┤
│   🚩 Report    ❓ Bantuan│
└─────────────────────────┘
```

### Mode Menunggu *(di antrian)*
```
┌────────────┐
│  🛑 Stop   │
├────────────┤
│ ❓ Bantuan │
└────────────┘
```

---

## 🏗️ Arsitektur Teknis

### Struktur Folder

```
Gaynonimous-Chat-Bot/
├── main.py                  ← Entry point, semua handler didaftarkan di sini
├── requirements.txt
├── Procfile                 ← worker: python main.py (Railway)
├── railway.toml             ← Konfigurasi build & deploy Railway
├── runtime.txt              ← Python 3.11.9
├── .env.example             ← Template environment variables
├── .gitignore
├── README.md
│
├── config/
│   └── settings.py          ← Load semua variabel dari .env
│
├── services/
│   ├── database.py          ← ORM SQLAlchemy (PostgreSQL + SQLite fallback)
│   ├── state_manager.py     ← State runtime: antrian, chat aktif, pending media, blokir
│   └── media_service.py     ← Kirim media + background cleanup expired approval
│
├── handlers/
│   ├── start.py             ← /start + sambutan + peringatan keamanan
│   ├── chat.py              ← Cari Partner, Stop Chat, Next Partner
│   ├── message_relay.py     ← Relay teks/stiker/voice; foto/video → approval flow
│   ├── media_approval.py    ← Callback InlineKeyboard Lihat Media / Tolak
│   ├── report.py            ← Report + auto-blokir partner
│   ├── profile.py           ← Profil anonim user
│   ├── help.py              ← Bantuan + edukasi keamanan
│   ├── admin.py             ← Semua perintah admin
│   └── queue_watcher.py     ← Background task: auto-match antrian tiap 2 detik
│
└── utils/
    ├── keyboards.py          ← Template semua keyboard
    └── messages.py           ← Semua teks pesan dalam Bahasa Indonesia
```

### State Management
Semua state runtime disimpan **di memori** menggunakan `asyncio.Lock` untuk keamanan konkurensi:

| State | Struktur | Isi |
|---|---|---|
| `_waiting_queue` | `Dict[int, datetime]` | User menunggu partner + waktu masuk antrian |
| `_active_chats` | `Dict[int, int]` | Pasangan chat aktif (bidirectional) |
| `_pending_media` | `Dict[str, PendingMedia]` | Media menunggu approval + waktu kadaluarsa |
| `_blocked` | `Dict[int, Set[int]]` | Daftar blokir antar user |

### Database
- **Lokal**: SQLite otomatis (`gaynonimous.db`) jika `DATABASE_URL` kosong
- **Production**: PostgreSQL via Railway, otomatis terhubung lewat `DATABASE_URL`
- Tabel: `users`, `reports`, `event_logs`

### Background Tasks
Dua task berjalan terus-menerus di background setelah bot start:

- **`queue_watcher`** — setiap 2 detik, coba cocokkan pasangan di antrian dengan mempertimbangkan daftar blokir
- **`cleanup_expired_media`** — setiap 10 detik, hapus pending media yang sudah melewati batas waktu dan notifikasi kedua pihak

---

## ☁️ Deploy ke Railway *(Tanpa Setup Lokal)*

### Langkah 1 — Hubungkan GitHub
1. Buka [railway.app](https://railway.app) → Login dengan akun GitHub
2. Klik **New Project** → **Deploy from GitHub repo**
3. Pilih repo **Gaynonimous-Chat-Bot**
4. Railway otomatis mendeteksi `Procfile` dan mulai proses build

### Langkah 2 — Tambah Database PostgreSQL
1. Di dalam project Railway, klik **+ New**
2. Pilih **Database** → **PostgreSQL**
3. Variabel `DATABASE_URL` akan **otomatis tersedia** di service bot — tidak perlu diisi manual

### Langkah 3 — Set Environment Variables
Masuk ke service bot → tab **Variables** → tambahkan:

| Variabel | Wajib | Contoh Nilai | Keterangan |
|---|---|---|---|
| `BOT_TOKEN` | ✅ Ya | `7123456789:AAFxxx...` | Dapatkan dari [@BotFather](https://t.me/BotFather) di Telegram |
| `ADMIN_IDS` | ✅ Ya | `123456789` | Telegram ID kamu. Cek via [@userinfobot](https://t.me/userinfobot). Untuk beberapa admin pisahkan koma: `111,222` |
| `DATABASE_URL` | ⚙️ Auto | *(jangan diisi)* | Otomatis diisi Railway dari plugin PostgreSQL |
| `MEDIA_APPROVAL_TIMEOUT` | ❌ Opsional | `60` | Detik sebelum pending media expired. Default: 60 |
| `LOG_LEVEL` | ❌ Opsional | `INFO` | Level log. Gunakan `DEBUG` untuk troubleshoot |

### Langkah 4 — Deploy
Railway otomatis redeploy setelah variabel disimpan. Cek tab **Deployments** → **Logs**:

```
Database siap.
Bot berjalan...
Background tasks dimulai.
```

Jika ketiga baris ini muncul, bot sudah online. ✅

> **Tips:** Setiap kali kamu push commit ke branch `main`, Railway otomatis redeploy tanpa tindakan manual.

---

## 💻 Setup Lokal *(untuk Development)*

```bash
# Clone repo
git clone https://github.com/gfrrmd/Gaynonimous-Chat-Bot.git
cd Gaynonimous-Chat-Bot

# Buat virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt

# Buat file .env
cp .env.example .env
# Buka .env dan isi BOT_TOKEN dan ADMIN_IDS
# DATABASE_URL dikosongkan → otomatis pakai SQLite lokal

# Jalankan bot
python main.py
```

Database SQLite (`gaynonimous.db`) akan otomatis dibuat di folder yang sama.

---

## 📦 Dependensi

| Library | Versi | Fungsi |
|---|---|---|
| `python-telegram-bot` | `>=21.0` | Telegram Bot API — polling, handler, callback |
| `sqlalchemy` | `>=2.0` | ORM database — model, query, session |
| `psycopg2-binary` | `>=2.9` | Driver koneksi PostgreSQL |
| `python-dotenv` | `>=1.0` | Load variabel dari file `.env` |

---

## 🔒 Keamanan & Privasi

- **Identitas tersembunyi** — tidak ada informasi pengguna yang dibagikan ke lawan bicara
- **Media tidak auto-forward** — semua foto/video memerlukan persetujuan eksplisit
- **Auto-expire** — pending media yang tidak direspons otomatis dihapus setelah 60 detik
- **Event logging** — semua aktivitas penting (start, chat, report, ban) dicatat di `event_logs`
- **Ban permanen** — admin dapat memblokir pengguna yang melanggar aturan

---

## 📄 Lisensi

Dirilis di bawah [MIT License](LICENSE). Bebas digunakan, dimodifikasi, dan didistribusikan.
