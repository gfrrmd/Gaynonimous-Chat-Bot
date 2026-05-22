"""
Handler relay pesan saat chat aktif.
- Teks, stiker, voice note -> langsung relay
- Foto, video, dokumen, animasi -> perlu approval
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.state_manager import state
from services.database import is_user_banned
from services.media_service import build_approval_keyboard
from utils.messages import MEDIA_APPROVAL_REQUEST, BANNED_MESSAGE

logger = logging.getLogger(__name__)

NOT_IN_CHAT_HINT = "\U0001f4ac _Kamu belum terhubung dengan siapapun. Tekan *Cari Partner* untuk mulai._"


async def relay_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_user_banned(user.id):
        await update.message.reply_text(BANNED_MESSAGE, parse_mode="Markdown")
        return

    partner_id = await state.get_partner(user.id)
    if not partner_id:
        await update.message.reply_text(NOT_IN_CHAT_HINT, parse_mode="Markdown")
        return

    try:
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    except Exception as e:
        logger.error(f"Gagal relay teks dari {user.id}: {e}")


async def relay_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    partner_id = await state.get_partner(user.id)
    if not partner_id:
        return
    try:
        await context.bot.send_sticker(chat_id=partner_id, sticker=update.message.sticker.file_id)
    except Exception as e:
        logger.error(f"Gagal relay stiker: {e}")


async def relay_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    partner_id = await state.get_partner(user.id)
    if not partner_id:
        return
    try:
        await context.bot.send_voice(chat_id=partner_id, voice=update.message.voice.file_id)
    except Exception as e:
        logger.error(f"Gagal relay voice note: {e}")


async def relay_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    partner_id = await state.get_partner(user.id)
    if not partner_id:
        return
    try:
        await context.bot.send_audio(chat_id=partner_id, audio=update.message.audio.file_id)
    except Exception as e:
        logger.error(f"Gagal relay audio: {e}")


async def handle_media_with_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk foto, video, dokumen, animasi - perlu approval."""
    user = update.effective_user
    if is_user_banned(user.id):
        await update.message.reply_text(BANNED_MESSAGE, parse_mode="Markdown")
        return

    partner_id = await state.get_partner(user.id)
    if not partner_id:
        await update.message.reply_text(NOT_IN_CHAT_HINT, parse_mode="Markdown")
        return

    msg = update.message
    file_id = None
    media_type = None
    caption = msg.caption

    if msg.photo:
        file_id = msg.photo[-1].file_id
        media_type = "photo"
    elif msg.video:
        file_id = msg.video.file_id
        media_type = "video"
    elif msg.animation:
        file_id = msg.animation.file_id
        media_type = "animation"
    elif msg.document:
        file_id = msg.document.file_id
        media_type = "document"

    if not file_id:
        return

    approval_id = await state.create_pending_media(
        sender_id=user.id,
        receiver_id=partner_id,
        file_id=file_id,
        media_type=media_type,
        caption=caption,
    )

    try:
        await context.bot.send_message(
            chat_id=partner_id,
            text=MEDIA_APPROVAL_REQUEST,
            parse_mode="Markdown",
            reply_markup=build_approval_keyboard(approval_id),
        )
        await update.message.reply_text(
            "\U0001f4e4 *Media kamu sedang menunggu persetujuan lawan bicara...*\n"
            "_Permintaan akan kadaluarsa dalam 60 detik jika tidak direspons._",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Gagal kirim approval request: {e}")
