"""Keyboard templates."""
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# ---- Teks Tombol ----
BTN_FIND = "\U0001f50d Cari Partner"
BTN_NEXT = "\u23ed Next Partner"
BTN_STOP = "\U0001f6d1 Stop Chat"
BTN_REPORT = "\U0001f6a9 Report User"
BTN_PROFILE = "\U0001f464 Profil Saya"
BTN_HELP = "\u2753 Bantuan"

BTN_VIEW_MEDIA = "\u2705 Lihat Media"
BTN_REJECT_MEDIA = "\u274c Tolak"

# ---- Tombol Admin ----
BTN_ADMIN_STATS = "\U0001f4ca Statistik"
BTN_ADMIN_REPORTS = "\U0001f6a9 Laporan"
BTN_ADMIN_BAN = "\U0001f6ab Ban User"
BTN_ADMIN_UNBAN = "\u2705 Unban User"
BTN_ADMIN_BROADCAST = "\U0001f4e2 Broadcast"


def main_keyboard() -> ReplyKeyboardMarkup:
    """Menu utama - tidak sedang chat."""
    return ReplyKeyboardMarkup(
        [
            [BTN_FIND],
            [BTN_PROFILE, BTN_HELP],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def chat_keyboard() -> ReplyKeyboardMarkup:
    """Mode saat sedang chat."""
    return ReplyKeyboardMarkup(
        [
            [BTN_NEXT, BTN_STOP],
            [BTN_REPORT, BTN_HELP],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def waiting_keyboard() -> ReplyKeyboardMarkup:
    """Sedang menunggu partner."""
    return ReplyKeyboardMarkup(
        [
            [BTN_STOP],
            [BTN_HELP],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def admin_keyboard() -> ReplyKeyboardMarkup:
    """Menu admin - tampil hanya untuk ADMIN_IDS."""
    return ReplyKeyboardMarkup(
        [
            [BTN_FIND],
            [BTN_PROFILE, BTN_HELP],
            [BTN_ADMIN_STATS, BTN_ADMIN_REPORTS],
            [BTN_ADMIN_BAN, BTN_ADMIN_UNBAN],
            [BTN_ADMIN_BROADCAST],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
