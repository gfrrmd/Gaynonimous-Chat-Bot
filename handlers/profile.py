"""Handler Profil Saya."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.database import get_or_create_user
from utils.keyboards import main_keyboard, admin_keyboard
from utils.messages import profile_text
from config.settings import ADMIN_IDS


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_or_create_user(user.id, user.username, user.first_name)
    member_since = db_user.created_at.strftime("%d %B %Y") if db_user.created_at else "Tidak diketahui"
    text = profile_text(user.id, db_user.total_chats, member_since)

    # Inline keyboard dengan aksi profil
    inline_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4ca Statistik Chat", callback_data="profile_stats")],
        [InlineKeyboardButton("\U0001f504 Refresh Profil", callback_data="profile_refresh")],
    ])

    if user.id in ADMIN_IDS:
        kb = admin_keyboard()
    else:
        kb = main_keyboard()

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=kb,
    )
    # Kirim inline keyboard terpisah agar tidak bentrok dengan ReplyKeyboard
    await update.message.reply_text(
        "_Pilih aksi di bawah:_",
        parse_mode="Markdown",
        reply_markup=inline_kb,
    )


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button dari profil."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    db_user = get_or_create_user(user.id, user.username, user.first_name)
    member_since = db_user.created_at.strftime("%d %B %Y") if db_user.created_at else "Tidak diketahui"

    if query.data == "profile_stats":
        text = (
            f"\U0001f4ca *Statistik Chat Kamu*\n\n"
            f"\U0001f4ac Total Obrolan: `{db_user.total_chats}`\n"
            f"\U0001f6a9 Total Laporan Diterima: `{db_user.report_count}`\n"
            f"\U0001f4c5 Bergabung: {member_since}\n"
        )
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="profile_refresh")]]))

    elif query.data == "profile_refresh":
        text = profile_text(user.id, db_user.total_chats, member_since)
        inline_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("\U0001f4ca Statistik Chat", callback_data="profile_stats")],
            [InlineKeyboardButton("\U0001f504 Refresh Profil", callback_data="profile_refresh")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=inline_kb)
