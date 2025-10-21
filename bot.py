import os
import socket
import threading
import atexit
import logging
import requests
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🧠 Диагностика запуска
start_time = datetime.now().isoformat()
host_name = socket.gethostname()
pid = os.getpid()

logging.basicConfig(level=logging.INFO)
logging.info(f"Bot started at {start_time} on host {host_name} with PID: {pid}")
atexit.register(lambda: logging.info(f"Bot with PID {os.getpid()} is shutting down"))

# 🔐 Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

if not TELEGRAM_TOKEN or not NEWSAPI_KEY:
    raise ValueError("Не найден TELEGRAM_TOKEN или NEWSAPI_KEY в .env")

# 📡 Компании
COMPANIES = [
    "OpenAI", "NVIDIA", "Google DeepMind", "Microsoft",
    "Amazon", "Meta", "Anthropic", "DeepSeek"
]

# 📰 Получение новостей
def get_news(query):
    try:
        url = f'https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get('articles', [])[:5]
        if not articles:
            return f"Нет свежих новостей по теме: {query}"
        news = ""
        for article in articles:
            title = article.get('title', 'Без названия')
            url = article.get('url', '')
            news += f"• {title}\n{url}\n\n"
        return news
    except Exception as e:
        logging.error(f"Ошибка при запросе новостей: {e}")
        return "⚠️ Не удалось получить новости. Попробуйте позже."

# 🎯 Кнопочные меню
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Latest News", callback_data="latest_news")],
        [InlineKeyboardButton("AI Companies", callback_data="companies_menu")]
    ])

def news_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Main Options", callback_data="main_menu")],
        [InlineKeyboardButton("AI Companies", callback_data="companies_menu")]
    ])

def companies_menu():
    buttons = [[InlineKeyboardButton("Main Options", callback_data="main_menu")]]
    for company in COMPANIES:
        buttons.append([InlineKeyboardButton(company, callback_data=f"company_{company}")])
    return InlineKeyboardMarkup(buttons)

def company_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Main Options", callback_data="main_menu")],
        [InlineKeyboardButton("AI Companies", callback_data="companies_menu")]
    ])

# 📲 Обработчики
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Главное меню:", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.edit_message_text("📍 Главное меню:", reply_markup=main_menu())

    elif data == "latest_news":
        await query.edit_message_text("🧠 Свежие новости по ИИ...", reply_markup=news_menu())
        news = get_news("artificial intelligence")
        await query.message.reply_text(news)

    elif data == "companies_menu":
        await query.edit_message_text("📋 Выберите компанию:", reply_markup=companies_menu())

    elif data.startswith("company_"):
        company = data.replace("company_", "")
        await query.edit_message_text(f"🏢 Новости по теме: {company}", reply_markup=company_menu())
        news = get_news(company)
        await query.message.reply_text(news)

# 🚀 Запуск приложения
is_running = False

def main():
    global is_running
    if is_running:
        logging.warning("Polling уже запущен — повторный запуск отменён")
        return
    is_running = True

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    logging.info("Handlers registered. Starting polling...")
    app.run_polling()

# 🧷 Защита от повторного запуска
if __name__ == "__main__":
    if threading.active_count() == 1:
        main()
    else:
        logging.warning("Polling already active — skipping duplicate start")
