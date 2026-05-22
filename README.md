# 🎭 Gaynonimous Chat Bot

Bot Telegram untuk anonymous chat 1-lawan-1 berbasis Python dengan keamanan media approval.

## ✨ Fitur Utama

- 🔍 **Matchmaking otomatis** — Cari partner random dari antrian
- 💬 **Anonymous chat** — Tidak ada yang tahu identitas aslimu
- 📎 **Media Approval** — Foto & video perlu disetujui partner sebelum terkirim
- 🛡️ **Keamanan** — Peringatan scam, blokir, dan laporan terintegrasi
- 👤 **Profil anonim** — Hanya menampilkan ID acak
- 🔧 **Admin panel** — Statistik, ban, broadcast, laporan

## 📁 Struktur Folder

```
gaynonimous-chat-bot/
├── main.py
├── requirements.txt
├── Procfile
├── railway.toml
├── runtime.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   └── settings.py
├── services/
│   ├── database.py
│   ├── state_manager.py
│   └── media_service.py
├── handlers/
│   ├── start.py
│   ├── chat.py
│   ├── message_relay.py
│   ├── media_approval.py
│   ├── report.py
│   ├── profile.py
│   ├── help.py
│   ├── admin.py
│   └── queue_watcher.py
└── utils/
    ├── keyboards.py
    └── messages.py
```

## 🚀 Setup Lokal

```bash
git clone https://github.com/gfrrmd/Gaynonimous-Chat-Bot.git
cd Gaynonimous-Chat-Bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: isi BOT_TOKEN dan ADMIN_IDS
python main.py
```

## ☁️ Deploy ke Railway

1. Push ke GitHub
2. Railway → **New Project** → **Deploy from GitHub repo**
3. Tambah plugin **PostgreSQL** (variabel `DATABASE_URL` otomatis diisi)
4. Set variabel: `BOT_TOKEN`, `ADMIN_IDS`, `MEDIA_APPROVAL_TIMEOUT=60`
5. Deploy otomatis via `Procfile` → `worker: python main.py`

## 🤖 Perintah Admin

| Perintah | Fungsi |
|---|---|
| `/admin_stats` | Statistik bot |
| `/admin_ban <user_id> [alasan]` | Ban user |
| `/admin_unban <user_id>` | Unban user |
| `/admin_broadcast <pesan>` | Broadcast ke semua user |
| `/admin_reports` | 10 laporan terbaru |

## 📱 Menu Keyboard

### Menu Utama
| Tombol | Fungsi |
|---|---|
| 🔍 Cari Partner | Masuk antrian pencarian |
| 👤 Profil Saya | Lihat profil anonim |
| ❓ Bantuan | Panduan + tips keamanan |

### Mode Chat
| Tombol | Fungsi |
|---|---|
| ⏭ Next Partner | Cari partner baru |
| 🛑 Stop Chat | Akhiri obrolan |
| 🚩 Report User | Laporkan + blokir partner |
| ❓ Bantuan | Panduan keamanan |

## 📦 Dependensi

| Library | Fungsi |
|---|---|
| `python-telegram-bot>=21.0` | Telegram Bot API |
| `sqlalchemy>=2.0` | ORM database |
| `psycopg2-binary` | Driver PostgreSQL |
| `python-dotenv` | Load `.env` |

## 📄 Lisensi

MIT License
