"""Handler Report User dan Block — dengan alasan wajib diketik."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.database import add_report, log_event
from services.state_manager import state
from utils.keyboards import main_keyboard, admin_keyboard
from utils.messages import REPORT_SENT, NOT_IN_CHAT, PARTNER_LEFT
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)

WAITING_REASON = 1  # State untuk ConversationHandler


async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Langkah 1: Cek apakah sedang chat, lalu minta alasan."""
    user = update.effective_user
    partner_id = await state.get_partner(user.id)

    if not partner_id:
        await update.message.reply_text(NOT_IN_CHAT, parse_mode="Markdown")
        return ConversationHandler.END

    # Simpan sementara siapa yang akan direport
    context.user_data["report_target"] = partner_id

    await update.message.reply_text(
        "⚠️ *Kamu akan melaporkan partner chat ini.*\n\n"
        "Tuliskan alasan report kamu (minimal 10 karakter).\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode="Markdown",
    )
    return WAITING_REASON


async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Langkah 2: Terima alasan, proses report."""
    user = update.effective_user
    reason = update.message.text.strip()

    if len(reason) < 10:
        await update.message.reply_text(
            "❌ Alasan terlalu singkat. Tolong jelaskan lebih detail (minimal 10 karakter)."
        )
        return WAITING_REASON  # Minta ulang

    partner_id = context.user_data.get("report_target")
    if not partner_id:
        await update.message.reply_text("❌ Sesi report tidak valid. Coba lagi.")
        return ConversationHandler.END

    add_report(reporter_id=user.id, reported_id=partner_id, reason=reason)
    log_event("report", user.id, f"reported={partner_id}, reason={reason}")

    await state.block_user(user.id, partner_id)
    await state.end_chat(user.id)
    context.user_data.pop("report_target", None)

    kb = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    await update.message.reply_text(
        f"✅ *Report berhasil dikirim!*\n\nAlasan: _{reason}_\n\n"
        "Terima kasih telah melaporkan dengan bertanggung jawab.",
        parse_mode="Markdown",
        reply_markup=kb,
    )

    try:
        partner_kb = admin_keyboard() if partner_id in ADMIN_IDS else main_keyboard()
        await context.bot.send_message(
            chat_id=partner_id,
            text=PARTNER_LEFT,
            parse_mode="Markdown",
            reply_markup=partner_kb,
        )
    except Exception:
        pass

    return ConversationHandler.END


async def cancel_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User membatalkan report."""
    context.user_data.pop("report_target", None)
    await update.message.reply_text("✅ Report dibatalkan.")
    return ConversationHandler.END
