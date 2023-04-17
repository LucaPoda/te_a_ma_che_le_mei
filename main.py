import datetime
import logging
from datetime import datetime
import db
import handlers

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:



    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


def main() -> None:
    db.init()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6159085177:AAHQjKTkPw5ob4nXQL6zxVLrXA1j9GGwijQ").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new_cost", handlers.new_cost))
    application.add_handler(CommandHandler("new_cost_past", handlers.new_cost_past))
    application.add_handler(CommandHandler("new_income", handlers.new_income))
    application.add_handler(CommandHandler("new_income_past", handlers.new_income_past))
    application.add_handler(CommandHandler("add_category", handlers.new_category))
    application.add_handler(CommandHandler("reset", handlers.reset))
    application.add_handler(CommandHandler("list_categories", handlers.list_categories))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.default))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()