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
    level=logging.DEBUG  # Изменено на DEBUG для более подробного логирования
)
logger = logging.getLogger(__name__)

# Получение токена бота
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")

logger.info(f"Bot token: {TOKEN[:20]}...")  # Логируем часть токена для проверки

# URL вашего веб-приложения
WEBAPP_URL = os.getenv('WEBAPP_URL', "https://dewa-1gdh.onrender.com")
logger.info(f"WebApp URL: {WEBAPP_URL}")

def create_main_keyboard():
    keyboard = [
        [KeyboardButton('🛍 Открыть приложение')],
        [KeyboardButton('👨‍💼 Админ-панель')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        logger.info(f"Start command received from user {update.effective_user.id}")
        
        keyboard = create_main_keyboard()
        
        await update.message.reply_text(
            "Добро пожаловать в Diwa store! 🎉\n"
            "Выберите действие из меню ниже:",
            reply_markup=keyboard
        )
        logger.info("Start command processed successfully")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def setup_commands_and_menu(application):
    """Настройка команд и меню бота"""
    try:
        logger.info("Setting up commands and menu...")
        commands = [
            BotCommand("start", "🚀 Запустить бота"),
            BotCommand("help", "ℹ️ Помощь"),
            BotCommand("catalog", "📱 Каталог товаров"),
            BotCommand("admin", "⚙️ Панель администратора"),
            BotCommand("openapp", "🛍 Открыть магазин")
        ]
        
        await application.bot.set_my_commands(commands)
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))
        )
        logger.info("Commands and menu setup completed")
        
    except Exception as e:
        logger.error(f"Error setting up commands and menu: {e}", exc_info=True)

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /openapp"""
    try:
        logger.info(f"OpenApp command received from user {update.effective_user.id}")
        keyboard = [[KeyboardButton("🛍 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Нажмите кнопку ниже, чтобы открыть магазин:",
            reply_markup=reply_markup
        )
        logger.info("OpenApp command processed successfully")
    except Exception as e:
        logger.error(f"Error in openapp command: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    try:
        logger.info(f"Help command received from user {update.effective_user.id}")
        await update.message.reply_text(
            "🤖 Список доступных команд:\n\n"
            "/start - Запустить бота\n"
            "/help - Показать это сообщение\n"
            "/catalog - Просмотр каталога\n"
            "/openapp - Открыть веб-приложение\n"
            "/admin - Панель администратора (если у вас есть доступ)\n\n"
            "Также вы можете использовать кнопки меню для навигации."
        )
        logger.info("Help command processed successfully")
    except Exception as e:
        logger.error(f"Error in help command: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /catalog"""
    try:
        logger.info(f"Catalog command received from user {update.effective_user.id}")
        keyboard = [
            [InlineKeyboardButton("👟 Обувь", callback_data="cat_shoes")],
            [InlineKeyboardButton("👕 Одежда", callback_data="cat_clothes")],
            [InlineKeyboardButton("👜 Аксессуары", callback_data="cat_accessories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📱 Выберите категорию:",
            reply_markup=reply_markup
        )
        logger.info("Catalog command processed successfully")
    except Exception as e:
        logger.error(f"Error in catalog command: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    try:
        query = update.callback_query
        logger.info(f"Button callback received: {query.data} from user {query.from_user.id}")
        
        # Обработка категорий
        if query.data.startswith("cat_"):
            category = query.data.split("_")[1]
            await query.answer(f"Выбрана категория: {category}")
            await query.edit_message_text(f"Показываю товары в категории {category}...")
            
        logger.info("Button callback processed successfully")
    except Exception as e:
        logger.error(f"Error in button handler: {e}", exc_info=True)
        await query.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    try:
        logger.info(f"Message received: {update.message.text} from user {update.effective_user.id}")
        if update.message.text == "📱 Каталог":
            await catalog_command(update, context)
        elif update.message.text == "ℹ️ Помощь":
            await help_command(update, context)
        elif update.message.text == "👤 Профиль":
            await update.message.reply_text("Функция профиля в разработке")
        elif update.message.text == "🛒 Корзина":
            await update.message.reply_text("Функция корзины в разработке")
        elif update.message.text == "👨‍💼 Админ-панель":
            await admin_panel(update, context)
        logger.info("Message processed successfully")
    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды админ-панели"""
    try:
        logger.info(f"Admin command received from user {update.effective_user.id}")
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        logger.info(f"Checking admin access for user_id: {user_id}, username: {username}")
        
        if is_admin(user_id, username):
            logger.info("Admin access granted")
            admin_url = "https://cwompu1.github.io/dewa/"
            keyboard = [[InlineKeyboardButton(
                text="🔐 Открыть админ-панель",
                url=admin_url
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Добро пожаловать в панель администратора! 👋\n"
                "Нажмите на кнопку ниже, чтобы открыть панель управления:",
                reply_markup=reply_markup
            )
            logger.info("Admin panel link sent successfully")
        else:
            logger.warning(f"Admin access denied for user_id: {user_id}, username: {username}")
            await update.message.reply_text("⛔️ У вас нет доступа к админ-панели.")
    except Exception as e:
        logger.error(f"Error in admin command: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

def is_admin(user_id, username=None):
    # Список ID администраторов
    admin_ids = [307233318]  # Ваш Telegram ID
    # Список username администраторов
    admin_usernames = ['gafurrovvv']
    
    if username and username.lower() in [u.lower() for u in admin_usernames]:
        return True
    return user_id in admin_ids

def main():
    """Основная функция запуска бота"""
    try:
        logger.info("Starting bot initialization...")
        
        # Создание и настройка бота с увеличенным таймаутом
        application = Application.builder().token(TOKEN).connect_timeout(30.0).read_timeout(30.0).write_timeout(30.0).build()
        logger.info("Application instance created")
        
        # Инициализация базы данных внутри контекста приложения
        with app.app_context():
            logger.info("Initializing database...")
            # Создаем таблицы если их нет
            db.create_all()
            logger.info("Database tables created")
            
            # Инициализируем админа
            Admin.init_superadmin()
            logger.info("Superadmin initialized")
            
            # Добавляем обработчики
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("catalog", catalog_command))
            application.add_handler(CommandHandler("openapp", open_app))
            application.add_handler(CallbackQueryHandler(button_handler))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            logger.info("Command handlers added")
            
            # Устанавливаем функцию настройки при старте
            application.post_init = setup_commands_and_menu
            
            # Регистрация админ-хендлеров
            setup_admin_handlers(application)
            logger.info("Admin handlers registered")
            
            # Запускаем бота
            logger.info("Starting polling...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except Exception as e:
        logger.error(f"Critical error in main: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main() 