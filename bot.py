import os
import socket
import threading
import atexit
import logging
import requests
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

start_time = datetime.now().isoformat()
host_name = socket.gethostname()
pid = os.getpid()

logging.basicConfig(level=logging.INFO)
logging.info(f"Bot started at {start_time} on host {host_name} with PID: {pid}")
atexit.register(lambda: logging.info(f"Bot with PID {os.getpid()} is shutting down"))

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

if not TELEGRAM_TOKEN or not NEWSAPI_KEY:
    raise ValueError("Не найден TELEGRAM_TOKEN или NEWSAPI_KEY в .env")

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

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Собираю свежие новости по ИИ...")
    news = get_news("artificial intelligence")
    await update.message.reply_text(news)

async def company_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите название компании. Пример: /company OpenAI")
        return
    company_name = " ".join(context.args)
    await update.message.reply_text(f"Ищу новости по теме: {company_name}...")
    news = get_news(company_name)
    await update.message.reply_text(news)

async def deepseek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ищу свежие новости о DeepSeek...")
    news = get_news("DeepSeek")
    await update.message.reply_text(news)

async def companies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    companies = [
        "OpenAI", "NVIDIA", "Google DeepMind", "Microsoft", "Amazon", "Meta", "Anthropic", "DeepSeek"
    ]
    message = "🔍 Поддерживаемые компании для фильтрации:\n" + "\n".join(f"• {c}" for c in companies)
    await update.message.reply_text(message)

is_running = False

def main():
    global is_running
    if is_running:
        logging.warning("Polling уже запущен — повторный запуск отменён")
        return
    is_running = True

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("company", company_command))
    app.add_handler(CommandHandler("deepseek", deepseek_command))
    app.add_handler(CommandHandler("companies", companies_command))
    logging.info("Handlers registered. Starting polling...")
    app.run_polling()

if __name__ == "__main__":
    if threading.active_count() == 1:
        main()
    else:
        logging.warning("Polling already active — skipping duplicate start")
