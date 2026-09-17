import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_ID = 6779224630
BOT_TOKEN = "8989846892:AAGl1SnrPoXgFpuFW-XMsYRJRAiTJHF8wRE"

def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO settings (key, value) VALUES ('bot_status', 'ON')''')
    conn.commit()
    conn.close()

init_db()

def get_bot_status():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='bot_status'")
    val = cursor.fetchone()
    conn.close()
    return val[0] if val else 'ON'

def set_bot_status(status):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key='bot_status'", (status,))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()
    conn.close()

    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🟢 Turn ON", callback_data="turn_on"), InlineKeyboardButton("🔴 Turn OFF", callback_data="turn_off")],
            [InlineKeyboardButton("📊 Bot Status", callback_data="status"), InlineKeyboardButton("👥 User List", callback_data="users")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Welcome Admin! Choose an option:", reply_markup=reply_markup)
    else:
        status = get_bot_status()
        if status == 'OFF':
            await update.message.reply_text("দুঃখিত, বর্তমানে বটটি বন্ধ রয়েছে। একটু পরে আবার চেষ্টা করুন।")
        else:
            await update.message.reply_text("আসসালামু আলাইকুম! আপনার বার্তাটি সফলভাবে প্রেরণ করা হয়েছে। এডমিন খুব শীঘ্রই আপনার সাথে যোগাযোগ করবেন।")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "turn_on":
        set_bot_status('ON')
        await query.edit_message_text("✅ Bot has been turned ON successfully.")
    elif query.data == "turn_off":
        set_bot_status('OFF')
        await query.edit_message_text("🔴 Bot has been turned OFF successfully.")
    elif query.data == "status":
        status = get_bot_status()
        await query.edit_message_text(f"ℹ️ Current Bot Status: {status}")
    elif query.data == "users":
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        await query.edit_message_text(f"👥 Total users interacted with bot: {count}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        return

    status = get_bot_status()
    if status == 'OFF':
        await update.message.reply_text("দুঃখিত, বটটি বর্তমানে অফলাইন আছে।")
        return

    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 New message from {user.first_name} (ID: {user.id}):\n\n{update.message.text}")
    await update.message.reply_text("ধন্যবাদ! আপনার মেসেজটি এডমিনের কাছে পাঠানো হয়েছে।")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
