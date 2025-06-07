import os
import telebot
import google.generativeai as genai # Библиотека для работы с Google AI

# --- Настройка Telegram ---
# Получаем токен Telegram-бота из переменных окружения
# Это безопаснее, чем вставлять его напрямую в код
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if TELEGRAM_BOT_TOKEN is None:
    print("Ошибка: Переменная окружения 'TELEGRAM_BOT_TOKEN' не установлена.")
    print("Пожалуйста, установите ее перед запуском. Например: export TELEGRAM_BOT_TOKEN='ВАШ_ТОКЕН'")
    exit()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# --- Настройка Google AI Studio (Gemini) ---
# Получаем API-ключ Google AI из переменных окружения
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if GOOGLE_API_KEY is None:
    print("Ошибка: Переменная окружения 'GOOGLE_API_KEY' не установлена.")
    print("Пожалуйста, установите ее перед запуском. Например: export GOOGLE_API_KEY='ВАШ_КЛЮЧ'")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

# Инициализируем модель Gemini
# Вы можете выбрать модель, которую вы использовали в AI Studio, например 'gemini-pro'
# Или 'gemini-pro-vision' для работы с изображениями
model = genai.GenerativeModel('gemini-pro')

# --- Обработчик сообщений Telegram ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, использующий модель Gemini. Просто напиши мне что-нибудь!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Отправляем текст сообщения пользователя в модель Gemini
        response = model.generate_content(message.text)
        # Получаем ответ от модели
        gemini_response_text = response.text

        # Отправляем ответ обратно в Telegram
        bot.reply_to(message, gemini_response_text)

    except Exception as e:
        # В случае ошибки отправляем сообщение об ошибке
        print(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Извини, произошла ошибка при обработке твоего запроса. Попробуй еще раз позже.")

# --- Запуск бота ---
if __name__ == '__main__':
    print("Бот запущен и ждет сообщений...")
    bot.polling(non_stop=True)