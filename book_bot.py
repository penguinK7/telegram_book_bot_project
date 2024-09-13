import os
import logging
from telebot import TeleBot, types
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

# Инициализация бота
bot = TeleBot(TELEGRAM_TOKEN)

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Список для хранения книг и голосов
books = []
votes = {}

# Переменная для отслеживания состояния
awaiting_book = False  # Флаг для отслеживания, ожидаем ли мы ввод книги

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет! Используйте /new_book для добавления книги.')

# Команда /new_book
@bot.message_handler(commands=['new_book'])
def new_book(message):
    global awaiting_book
    awaiting_book = True  # Устанавливаем флаг, что ожидаем ввод книги
    bot.reply_to(message, 'Введите название и автора книги в формате "Название - Автор".')

# Обработка текстовых сообщений (книг)
@bot.message_handler(func=lambda message: awaiting_book)
def receive_book(message):
    global awaiting_book
    book_info = message.text
    books.append(book_info)  # Сохраняем книгу
    awaiting_book = False  # Сбрасываем флаг
    bot.reply_to(message, f'Книга "{book_info}" добавлена. Теперь вы можете ввести /new_book для добавления еще одной книги.')

# Команда /vote
@bot.message_handler(commands=['vote'])
def vote(message):
    if not books:
        bot.reply_to(message, 'Книги еще не добавлены. Пожалуйста, используйте /new_book для добавления книги.')
        return

    # Создаем кнопки для голосования
    keyboard = types.InlineKeyboardMarkup()
    for idx, book in enumerate(books, start=1):
        keyboard.add(types.InlineKeyboardButton(text=book, callback_data=f'vote_{idx}'))

    bot.send_message(CHAT_ID, 'Проголосуйте за книгу:', reply_markup=keyboard)

# Обработка голосов
@bot.callback_query_handler(func=lambda call: call.data.startswith('vote_'))
def handle_vote(call):
    vote_number = int(call.data.split('_')[1]) - 1
    if 0 <= vote_number < len(books):
        if books[vote_number] in votes:
            votes[books[vote_number]] += 1
        else:
            votes[books[vote_number]] = 1

        # Закрываем голосование для пользователя
        bot.answer_callback_query(call.id, f'Ваш голос за "{books[vote_number]}" принят!')
        bot.edit_message_text(text=f'Ваш голос за "{books[vote_number]}" принят!', chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(call.id, 'Пожалуйста, введите корректный номер книги.')

# Команда /result
@bot.message_handler(commands=['result'])
def result(message):
    if not votes:
        bot.reply_to(message, 'Голосование еще не проводилось.')
        return

    max_votes = max(votes.values())
    winners = [book for book, count in votes.items() if count == max_votes]

    if len(winners) == 1:
        bot.reply_to(message, f'Победила книга: "{winners[0]}" с {max_votes} голосом(ами).')
    else:
        bot.reply_to(message, f'Победили книги: {", ".join(winners)} с {max_votes} голосом(ами).')

# Команда /clear
@bot.message_handler(commands=['clear'])
def clear_books(message):
    global books, votes
    books.clear()
    votes.clear()
    bot.reply_to(message, 'Список книг и результаты голосования очищены.')

# Игнорируем все текстовые сообщения, кроме тех, которые идут после /new_book
@bot.message_handler(func=lambda message: True)
def ignore_messages(message):
    # Ничего не делаем, просто игнорируем
    pass

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)