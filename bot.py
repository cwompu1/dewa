import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, MenuButtonWebApp, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from handlers.admin import setup_admin_handlers
from models.admin import Admin
from database import db, app, init_db

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена бота
TOKEN = os.getenv('BOT_TOKEN')

# URL вашего веб-приложения
WEBAPP_URL = "https://dewa-1gdh.onrender.com"

async def setup_commands_and_menu(application):
    """Устанавливает команды и меню бота при старте"""
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("catalog", "Показать каталог товаров"),
        BotCommand("openapp", "Открыть веб-приложение"),
        BotCommand("admin", "Панель администратора")
    ]
    
    # Установка команд бота
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")
    
    # Установка кнопки меню
    try:
        menu_button = MenuButtonWebApp(text="ОТКРЫТЬ", web_app=WebAppInfo(url=WEBAPP_URL))
        await application.bot.set_chat_menu_button(menu_button=menu_button)
        logger.info("Menu button set successfully")
    except Exception as e:
        logger.error(f"Error setting menu button: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        # Создаем inline клавиатуру для категорий
        inline_keyboard = [
            [
                InlineKeyboardButton("👟 Обувь", callback_data='category_shoes'),
                InlineKeyboardButton("👕 Одежда", callback_data='category_clothes')
            ],
            [
                InlineKeyboardButton("👜 Аксессуары", callback_data='category_accessories'),
                InlineKeyboardButton("🛒 Корзина", callback_data='cart')
            ]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        # Создаем клавиатуру с кнопкой веб-приложения внизу экрана
        keyboard = [[KeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Отправляем приветственное сообщение с inline клавиатурой
        await update.message.reply_text(
            "👋 Добро пожаловать в наш магазин!\n\n"
            "Здесь вы найдете оригинальные товары по самым выгодным ценам.\n\n"
            "Выберите категорию товаров:",
            reply_markup=inline_markup
        )
        
        # Устанавливаем клавиатуру с кнопкой веб-приложения
        await update.message.reply_text(
            "Используйте кнопку ниже для быстрого доступа к приложению:",
            reply_markup=reply_markup
        )
        
        # Повторная установка кнопки меню для конкретного пользователя
        try:
            menu_button = MenuButtonWebApp(text="ОТКРЫТЬ", web_app=WebAppInfo(url=WEBAPP_URL))
            await context.bot.set_chat_menu_button(
                chat_id=update.effective_chat.id,
                menu_button=menu_button
            )
        except Exception as e:
            logger.error(f"Error setting menu button for user: {e}")
        
        logger.info(f"User {update.effective_user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /openapp"""
    try:
        # Создаем клавиатуру с кнопкой веб-приложения внизу экрана
        keyboard = [[KeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Нажмите кнопку ниже, чтобы открыть приложение:", 
            reply_markup=reply_markup
        )
        logger.info(f"User {update.effective_user.id} requested to open app")
    except Exception as e:
        logger.error(f"Error in open_app command: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    try:
        # Сначала отправляем текст справки
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/catalog - Показать каталог товаров\n"
            "/openapp - Открыть веб-приложение"
        )
        
        # Создаем клавиатуру с кнопкой веб-приложения внизу экрана
        keyboard = [[KeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Или используйте кнопку ниже:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /catalog"""
    try:
        inline_keyboard = [
            [
                InlineKeyboardButton("👟 Обувь", callback_data='category_shoes'),
                InlineKeyboardButton("👕 Одежда", callback_data='category_clothes')
            ],
            [
                InlineKeyboardButton("👜 Аксессуары", callback_data='category_accessories'),
                InlineKeyboardButton("🛒 Корзина", callback_data='cart')
            ]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        # Создаем клавиатуру с кнопкой веб-приложения внизу экрана
        keyboard = [[KeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text("Выберите категорию товаров:", reply_markup=inline_markup)
        
        # Устанавливаем клавиатуру с кнопкой веб-приложения
        await update.message.reply_text(
            "Или используйте кнопку WebApp:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in catalog command: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('category_'):
            category = query.data.split('_')[1]
            await query.message.reply_text(f"Вы выбрали категорию: {category}")
        elif query.data == 'cart':
            await query.message.reply_text("Ваша корзина пуста")
    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await query.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    try:
        text = update.message.text.lower()
        if text in ['привет', 'hello', 'hi']:
            await update.message.reply_text("Привет! Используйте /start для начала работы с ботом.")
        elif text == 'open app':
            await open_app(update, context)
        else:
            # Создаем клавиатуру с кнопкой веб-приложения внизу экрана
            keyboard = [[KeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "Используйте /start для начала работы с ботом или /help для просмотра доступных команд.",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in message handler: {e}")

def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация базы данных внутри контекста приложения
        with app.app_context():
            init_db()
            
            # Создание и настройка бота
            application = Application.builder().token(TOKEN).build()
            
            # Добавляем обработчики
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("catalog", catalog_command))
            application.add_handler(CommandHandler("openapp", open_app))
            application.add_handler(CallbackQueryHandler(button_handler))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Устанавливаем функцию настройки при старте
            application.post_init = setup_commands_and_menu
            
            # Регистрация админ-хендлеров
            setup_admin_handlers(application)
            
            # Запускаем бота
            logger.info("Starting bot...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main() 