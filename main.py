from datetime import datetime
from typing import Final
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from dao import DAO
from entry_data import EntryData

TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
DATABASE_URI: Final = os.getenv("DATABASE_URI")

# logging configurations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dao = DAO(DATABASE_URI)


# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to FINAX!')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Enter your message in the format:\n''<username> <user ID> <draw> <entry> <type id> <amount> <b / s>')


# responses
def parse_message(message: str):
    """
    :param message: Parse user message into components
    :return: <username> <user_id> <draw_id> <entry> <bet_type_id> <multiplier> <entry_size>
    """

    parts = message.split()

    if len(parts) != 7:
        raise ValueError("Invalid message format. Please enter /help for message format.")

    username = parts[0]
    user_id = int(parts[1])
    draw_id = int(parts[2])
    entry = parts[3]
    bet_type_id = int(parts[4])
    multiplier = int(parts[5])
    entry_size = parts[6]

    return username, user_id, draw_id, entry, bet_type_id, multiplier, entry_size


def insert_entry_to_db(user_id, draw_id, entry, bet_type_id, multiplier, entry_size):
    """
    Inserts an entry in the database using DAO and returns the processed entry data
    """

    try:
        result_row = dao.insert_entry(entry, entry_size, multiplier, user_id, bet_type_id, draw_id)
        logger.info(f"Database returned row: {result_row}")
        entry_data = EntryData(result_row)
        return entry_data
    except Exception as err:
        logger.error(f"Error inserting entry: {err}")
        raise


# handlers
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text.strip()
    message_type: str = update.message.chat.type
    chat_id = update.message.chat.id

    logger.info(f"User ({chat_id}) in {message_type}: '{text}'")

    if message_type == 'group' and BOT_USERNAME not in text:
        return

    # remove bot username in group messages
    if BOT_USERNAME in text:
        text = text.replace(BOT_USERNAME, '').strip()

    try:
        # parse the message
        username, user_id, draw_id, entry, bet_type_id, multiplier, entry_size = parse_message(text)

        # insert in database
        entry_data = insert_entry_to_db(user_id=user_id, draw_id=draw_id, entry=entry, bet_type_id=bet_type_id, multiplier=multiplier, entry_size=entry_size)

        # format the response
        response = f"✅ Entry recorded successfully!\n{entry_data}"
    except ValueError as value_err:
        logger.error(f"Message parsing error: {value_err}")
        response = f"❌ Error: {value_err}"
    except Exception as err:
        logger.error(f"Server error: {err}")
        response = "❌ An error occurred while processing your entry. Please try again later."

    logger.info(f"Bot response to ({chat_id}): {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_response))

    # error
    app.add_error_handler(error)

    # polling
    logger.info("Polling...")
    app.run_polling(poll_interval=3)
