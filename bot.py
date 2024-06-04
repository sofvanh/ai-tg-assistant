import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from anthropic import AsyncAnthropic

allowed_users = os.getenv("ALLOWED_USERS").split(",")
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.username not in allowed_users:
        await update.message.reply_text("You are not allowed to use this bot")
        return

    user_message = {
        "role": "user",
        "content": update.message.text,
    }

    message = await client.messages.create(
        max_tokens=1024,
        messages=[user_message],
        model="claude-3-opus-20240229",
        system="You are a personal AI assistant, talking to the user via the Telegram instant messaging app. Your messages should be as clear, helpful, short, and to-the-point as possible, similar to how text messages are normally sent.",
    )

    content_blocks = message.content
    message_text = "\n".join(block.text for block in content_blocks)

    await update.message.reply_text(message_text)


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_KEY")).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("\nBot started\n")

app.run_polling()

print("\nBot shutting down\n")
