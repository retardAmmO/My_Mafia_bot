import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Импортируем CORS
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализация Flask-приложения
app = Flask(__name__)
CORS(app) # Применяем CORS ко всем маршрутам (для разработки)
          # Для продакшена можно настроить более строго: CORS(app, resources={r"/api/*": {"origins": "URL_ВАШЕГО_FRONTEND"}})


# Получаем токен бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    print("Ошибка: Переменная окружения TELEGRAM_BOT_TOKEN не найдена!")
    # В реальном приложении здесь можно предпринять более серьезные действия
    # Например, завершить работу сервера, если токен критически важен.
    bot_instance = None
else:
    # Инициализация Telegram-бота
    bot_instance = Bot(token=TELEGRAM_BOT_TOKEN)

# API-эндпоинт для приема конфигурации игры
@app.route('/api/receive-mafia-config', methods=['POST'])
def receive_mafia_config():
    if not bot_instance:
        return jsonify({"error": "Telegram бот не инициализирован на сервере (проблема с токеном)."}), 500

    try:
        # Получаем JSON-данные из тела запроса
        data = request.get_json()

        if not data:
            return jsonify({"error": "Отсутствуют данные в запросе (No data in request)"}), 400

        # Извлекаем необходимые поля из JSON
        game_start_message = data.get('gameStartMessage')
        player_count = data.get('playerCount')
        role_summary = data.get('roleSummary') # [{ "name": "Роль", "count": N }, ...]
        assignments = data.get('assignments')   # [{ "player": "Игрок N", "role": "Название Роли", ...}, ...]
        telegram_chat_id = data.get('telegramChatId') # Это Chat ID, куда бот должен отправить сообщение

        # Проверяем наличие обязательных полей
        if not all([game_start_message, assignments, telegram_chat_id]):
            missing_fields = []
            if not game_start_message: missing_fields.append("gameStartMessage")
            if not assignments: missing_fields.append("assignments")
            if not telegram_chat_id: missing_fields.append("telegramChatId")
            return jsonify({"error": f"Отсутствуют обязательные поля в JSON: {', '.join(missing_fields)}"}), 400
        
        # Формируем сообщение для Telegram
        # 1. Тематическое сообщение
        message_to_send = f"✨🎲 *Конфигурация для новой игры в Мафию готова!* 🎲✨\n\n"
        message_to_send += f"{game_start_message}\n\n"

        # 2. Сводка по ролям (если есть)
        if player_count:
             message_to_send += f"👥 *Общее количество игроков:* {player_count}\n"
        if role_summary:
            message_to_send += "📋 *Состав ролей:*\n"
            for role_info in role_summary:
                message_to_send += f"  - {role_info.get('name', 'Неизвестная роль')}: {role_info.get('count', 0)}\n"
            message_to_send += "\n"
        
        # 3. Полное распределение ролей
        message_to_send += "🤫 *Распределение ролей для ведущего:*\n"
        for assignment in assignments:
            player_id = assignment.get('player', 'Неизвестный игрок')
            role_name = assignment.get('role', 'Неизвестная роль')
            alignment = assignment.get('alignment', '')
            message_to_send += f"  - {player_id}: *{role_name}* "
            if alignment:
                message_to_send += f"({alignment})"
            message_to_send += "\n"
        
        message_to_send += f"\n\n🤖 _Это сообщение отправлено автоматически конфигуратором ролей._"

        # Отправляем сообщение в Telegram
        try:
            bot_instance.send_message(
                chat_id=telegram_chat_id, 
                text=message_to_send,
                parse_mode='Markdown' # Используем Markdown для форматирования
            )
            print(f"Сообщение успешно отправлено в чат {telegram_chat_id}")
            return jsonify({"success": True, "message": "Конфигурация успешно получена и отправлена в Telegram."}), 200
        except TelegramError as e:
            print(f"Ошибка отправки сообщения в Telegram: {e}")
            return jsonify({"error": f"Ошибка отправки сообщения в Telegram: {str(e)}"}), 500
        except Exception as e:
            print(f"Непредвиденная ошибка при отправке в Telegram: {e}")
            return jsonify({"error": f"Непредвиденная ошибка при отправке в Telegram: {str(e)}"}), 500

    except Exception as e:
        print(f"Общая ошибка обработки запроса: {e}")
        # В реальном приложении здесь стоит логировать ошибку подробнее
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500

# Запуск Flask-сервера
if __name__ == '__main__':
    # Для разработки используйте debug=True. Для продакшена установите debug=False.
    # host='0.0.0.0' делает сервер доступным извне (не только с localhost)
    app.run(host='0.0.0.0', port=5000, debug=True)