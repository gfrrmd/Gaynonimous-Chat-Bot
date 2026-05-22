"""
Admin handler.
Semua perintah admin hanya bisa diakses oleh user yang ada di ADMIN_IDS.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.database import (
    get_stats, ban_user, unban_user, get_recent_reports, log_event
)
from services.state_manager import state
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("\u274c Kamu bukan admin.")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_only
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    queue_count = await state.queue_count()
    active = await state.active_chat_count()
    pending_media = await state.pending_media_count()

    text = (
        "\U0001f4ca *Statistik Bot*\n\n"
        f"\U0001f465 Total User: `{stats['total_users']}`\n"
        f"\U0001f6ab User Banned: `{stats['banned_users']}`\n"
        f"\u23f3 Antrian: `{queue_count}`\n"
        f"\U0001f4ac Chat Aktif: `{active}`\n"
        f"\U0001f4ce Pending Media: `{pending_media}`\n"
        f"\U0001f6a9 Total Laporan: `{stats['total_reports']}`\n"
        f"\U0001f534 Laporan Belum Ditinjau: `{stats['pending_reports']}`\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


@admin_only
async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /admin_ban <user_id> [alasan]"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /admin_ban <user_id> [alasan]")
        return
    try:
        target_id = int(args[0])
        reason = " ".join(args[1:]) if len(args) > 1 else "Dibanned oleh admin"
        ban_user(target_id, reason)
        log_event("admin_ban", update.effective_user.id, f"target={target_id} reason={reason}")
        await update.message.reply_text(f"\u2705 User `{target_id}` berhasil dibanned.\nAlasan: {reason}", parse_mode="Markdown")
        await state.end_chat(target_id)
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="\U0001f6ab *Akun kamu telah dibanned oleh admin.*",
                parse_mode="Markdown",
            )
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("\u274c User ID tidak valid.")


@admin_only
async def admin_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /admin_unban <user_id>"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /admin_unban <user_id>")
        return
    try:
        target_id = int(args[0])
        unban_user(target_id)
        log_event("admin_unban", update.effective_user.id, f"target={target_id}")
        await update.message.reply_text(f"\u2705 User `{target_id}` berhasil di-unban.", parse_mode="Markdown")
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="\u2705 *Akun kamu telah di-unban. Kamu bisa menggunakan bot lagi.*",
                parse_mode="Markdown",
            )
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("\u274c User ID tidak valid.")


@admin_only
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast pesan ke semua user. Usage: /admin_broadcast <pesan>"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /admin_broadcast <pesan>")
        return

    message = " ".join(args)
    from services.database import get_session, User

    with get_session() as session:
        users = session.query(User).filter_by(is_banned=False).all()
        user_ids = [u.telegram_id for u in users]

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"\U0001f4e2 *Pengumuman dari Admin:*\n\n{message}",
                parse_mode="Markdown",
            )
            sent += 1
        except Exception:
            failed += 1

    log_event("broadcast", update.effective_user.id, f"sent={sent} failed={failed}")
    await update.message.reply_text(f"\u2705 Broadcast selesai.\nTerkirim: {sent} | Gagal: {failed}")


@admin_only
async def admin_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan 10 laporan terbaru."""
    reports = get_recent_reports(10)
    if not reports:
        await update.message.reply_text("\u2705 Belum ada laporan.")
        return

    lines = ["\U0001f6a9 *10 Laporan Terbaru:*\n"]
    for r in reports:
        status = "\u2705" if r.reviewed else "\U0001f534"
        lines.append(
            f"{status} ID#{r.id} | Reporter: `{r.reporter_id}` \u2192 Dilaporkan: `{r.reported_id}`\n"
            f"   Alasan: {r.reason or '-'} | {r.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
