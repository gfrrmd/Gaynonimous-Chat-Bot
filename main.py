"""
Entry point - Gaynonimous Chat Bot
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters,
)
from config.settings import BOT_TOKEN, LOG_LEVEL
from services.database import init_db
from services.media_service import cleanup_expired_media
from handlers.queue_watcher import queue_watcher

from handlers.start import start_handler
from handlers.chat import find_partner, stop_chat, next_partner
from handlers.message_relay import (
    relay_text, relay_sticker, relay_voice, relay_audio,
    handle_media_with_approval,
)
from handlers.media_approval import media_callback
from handlers.report import report_handler
from handlers.profile import profile_handler
from handlers.help import help_handler
from handlers.admin import (
    admin_stats, admin_ban, admin_unban, admin_broadcast, admin_reports
)
from utils.keyboards import (
    BTN_FIND, BTN_NEXT, BTN_STOP, BTN_REPORT, BTN_PROFILE, BTN_HELP
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Jalankan background tasks setelah bot siap."""
    bot = application.bot
    asyncio.create_task(cleanup_expired_media(bot))
    asyncio.create_task(queue_watcher(bot))
    logger.info("Background tasks dimulai.")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN belum diset di .env!")

    init_db()
    logger.info("Database siap.")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ---- Command Handlers ----
    app.add_handler(CommandHandler("start", start_handler))

    # Admin commands
    app.add_handler(CommandHandler("admin_stats", admin_stats))
    app.add_handler(CommandHandler("admin_ban", admin_ban))
    app.add_handler(CommandHandler("admin_unban", admin_unban))
    app.add_handler(CommandHandler("admin_broadcast", admin_broadcast))
    app.add_handler(CommandHandler("admin_reports", admin_reports))

    # ---- ReplyKeyboard Button Handlers ----
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_FIND}$"), find_partner))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NEXT}$"), next_partner))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_STOP}$"), stop_chat))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_REPORT}$"), report_handler))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), profile_handler))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_HELP}$"), help_handler))

    # ---- Media Approval Callback ----
    app.add_handler(CallbackQueryHandler(media_callback, pattern="^(approve_media|reject_media):"))

    # ---- Message Relay Handlers ----
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay_text))
    app.add_handler(MessageHandler(filters.Sticker.ALL, relay_sticker))
    app.add_handler(MessageHandler(filters.VOICE, relay_voice))
    app.add_handler(MessageHandler(filters.AUDIO, relay_audio))
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.ANIMATION,
        handle_media_with_approval,
    ))

    logger.info("Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
