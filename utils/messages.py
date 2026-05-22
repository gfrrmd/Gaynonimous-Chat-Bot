"""Teks pesan standar Bahasa Indonesia."""

WELCOME = (
    "\U0001f3ad *Selamat datang di Gaynonimous Chat!*\n\n"
    "Obrolan anonim 1-lawan-1 tanpa identitas.\n\n"
    "\u26a0\ufe0f Jangan bagikan data pribadi, klik link asing, atau kirim uang ke siapapun.\n\n"
    "Tekan *Cari Partner* untuk mulai ngobrol! \U0001f389"
)

HELP = (
    "\u2753 *Bantuan*\n\n"
    "\u2022 *Cari Partner* \u2014 mulai cari lawan bicara\n"
    "\u2022 *Next Partner* \u2014 ganti ke orang baru\n"
    "\u2022 *Stop Chat* \u2014 akhiri obrolan\n"
    "\u2022 *Report User* \u2014 laporkan pelanggaran\n"
    "\u2022 Foto/video butuh persetujuan penerima\n\n"
    "\U0001f512 Jaga privasi: jangan bagi nomor HP, alamat, atau data pribadi. "
    "Jika merasa tidak aman, *Stop Chat* lalu *Report User*. \U0001f499"
)

SEARCHING = (
    "\U0001f50d *Sedang mencari partner...*\n"
    "Kamu akan otomatis terhubung saat ada yang tersedia.\n\n"
    "Tekan *Stop* untuk batal."
)

PARTNER_FOUND = (
    "\U0001f389 *Partner ditemukan!*\n"
    "Mulai ngobrol sekarang. \U0001f4ac\n"
    "_Jaga privasimu dan hormati lawan bicara._"
)

PARTNER_LEFT = (
    "\U0001f44b *Lawan bicara meninggalkan obrolan.*\n"
    "Tekan *Cari Partner* untuk mencari orang baru."
)

CHAT_ENDED_BY_YOU = (
    "\U0001f6d1 *Obrolan diakhiri.*\n"
    "Tekan *Cari Partner* kapan saja untuk mulai lagi."
)

NEXT_SEARCHING = (
    "\u23ed *Mencari partner baru...*\n"
    "Koneksi sebelumnya telah diakhiri."
)

MEDIA_APPROVAL_REQUEST = (
    "\U0001f4ce *Lawan bicara ingin mengirim media.*\n\n"
    "\u26a0\ufe0f Media mungkin mengandung konten sensitif. Ingin melihatnya?"
)

MEDIA_APPROVED_SENDER = "\u2705 *Media kamu telah diterima dan dikirimkan!*"
MEDIA_REJECTED_SENDER = "\u274c *Lawan bicara menolak media yang kamu kirim.*"
MEDIA_APPROVED_RECEIVER = "\U0001f4ce *Berikut media dari lawan bicara:*"
MEDIA_REJECTED_RECEIVER = "\u2705 *Kamu berhasil menolak media tersebut.*"

REPORT_SENT = (
    "\U0001f6a9 *Laporan dikirim ke admin.*\n"
    "Terima kasih! Obrolan telah diakhiri dan user dicatat."
)

BANNED_MESSAGE = (
    "\U0001f6ab *Akun kamu telah dibanned.*\n"
    "Hubungi admin jika ini kesalahan."
)

NOT_IN_CHAT = "\u274c Kamu tidak sedang dalam obrolan."
ALREADY_IN_QUEUE = "\u23f3 Kamu sudah dalam antrian. Harap tunggu..."
ALREADY_IN_CHAT = "\U0001f4ac Kamu sudah dalam obrolan. Akhiri dulu untuk mencari partner baru."


def profile_text(user_id: int, total_chats: int, member_since: str) -> str:
    stars = "\u2b50" * min(5, max(1, total_chats // 5))
    return (
        f"\U0001f464 *Profil Kamu*\n\n"
        f"\U0001f194 ID Anonim: `#{user_id % 99999:05d}`\n"
        f"\U0001f4ac Total Obrolan: `{total_chats}`\n"
        f"\U0001f4c5 Bergabung: {member_since}\n"
        f"\U0001f3c6 Reputasi: {stars} ({total_chats} chat)\n\n"
        f"_Identitas aslimu tetap tersembunyi dari semua pengguna._"
    )
