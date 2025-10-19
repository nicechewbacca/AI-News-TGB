import os
import socket
from datetime import datetime

start_time = datetime.now().isoformat()
host_name = socket.gethostname()
pid = os.getpid()

print(f"Bot started at {start_time} on host {host_name} with PID: {pid}")

import atexit
atexit.register(lambda: print(f"Bot with PID {os.getpid()} is shutting down"))

import logging
logging.basicConfig(level=logging.INFO)
logging.info(f"Bot started at {start_time} on host {host_name} with PID: {pid}")
import requests
import urllib.parse
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_news(query):
    url = f'https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}'
    response = requests.get(url).json()
    articles = response.get('articles', [])[:5]
    news = ""
    for article in articles:
        title = article['title']
        url = article['url']
        news += f"• {title}\n{url}\n\n"
    return news or f"Нет свежих новостей по теме: {query}"

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

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("company", company_command))
    app.add_handler(CommandHandler("deepseek", deepseek_command))
    app.add_handler(CommandHandler("companies", companies_command))
    app.run_polling()

if __name__ == "__main__":
    import threading
    if threading.active_count() == 1:
        main()
    else:
        print("Polling already active — skipping duplicate start")



