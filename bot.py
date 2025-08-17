import time
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== CONFIG ======
BOT_TOKEN = "8046747342:AAFQ1a523b8WltQwDFwH6PuL7MV1lFdMrkU"
OWNER_IDS = [7851997598, 7788135096, 7383542259]  # Owner IDs
GROUP_ID = -1002662393368  # Test group ID

# Store active passwords
active_passwords = {}  # password: expiry_time

# ====== COMMANDS ======
async def genpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ You are not authorized to generate passwords!")
        return

    try:
        password = context.args[0]
        if context.args[1] != "validity":
            await update.message.reply_text("❌ Usage: /genpass <password> validity <time_in_seconds>")
            return
        validity = int(context.args[2])
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /genpass <password> validity <time_in_seconds>")
        return

    expiry_time = time.time() + validity
    active_passwords[password] = expiry_time

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"🔑 New Activation Password:\n`{password}`\n⏱ Valid for: {validity} seconds",
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ Password `{password}` generated for {validity} seconds and sent to group.")

# Check expired passwords periodically
async def check_expired(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    expired = [p for p, t in active_passwords.items() if t < now]
    for p in expired:
        del active_passwords[p]

# ====== BOT SETUP ======
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("genpass", genpass))

# Job to clean expired passwords every 10 seconds
app.job_queue.run_repeating(check_expired, interval=10, first=10)

print("Bot is running...")
app.run_polling()
