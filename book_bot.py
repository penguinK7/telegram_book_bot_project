import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Список для хранения книг и голосов
books = []
votes = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Используйте /new_book для добавления книги.')

# Команда /new_book
async def new_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите название и автора книги в формате "Название - Автор".')

# Обработка текстовых сообщений (книг)
async def receive_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    book_info = update.message.text
    books.append(book_info)  # Сохраняем книгу
    await update.message.reply_text(f'Книга "{book_info}" добавлена. Теперь вы можете ввести /new_book для добавления еще одной книги. Или /vote для голосования.')

# Команда /vote
async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not books:
        await update.message.reply_text('Книги еще не добавлены. Пожалуйста, используйте /new_book для добавления книги.')
        return

    # Создаем кнопки для голосования
    keyboard = [[InlineKeyboardButton(book, callback_data=book) for book in books]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Проголосуйте за книгу:', reply_markup=reply_markup)

# Обработка голосов
async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    book_title = query.data
    if book_title in votes:
        votes[book_title] += 1
    else:
        votes[book_title] = 1

    await query.edit_message_text(text=f'Ваш голос за "{book_title}" принят!')

# Команда /result
async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not votes:
        await update.message.reply_text('Голосование еще не проводилось.')
        return

    # Подсчитываем результаты
    max_votes = max(votes.values())
    winners = [book for book, count in votes.items() if count == max_votes]

    if len(winners) == 1:
        await update.message.reply_text(f'Победила книга: "{winners[0]}" с {max_votes} голосом(ами).')
    else:
        await update.message.reply_text(f'Победили книги: {", ".join(winners)} с {max_votes} голосом(ами).')

# Основная функция
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_book", new_book))
    application.add_handler(CommandHandler("vote", vote))
    application.add_handler(CommandHandler("result", result))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_book))
    application.add_handler(CallbackQueryHandler(handle_vote))  # Обработка нажатий на кнопки

    # Запускаем бота
    application.run_polling()