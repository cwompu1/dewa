from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from models.admin import Admin
from database import db

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin"""
    user = update.effective_user
    admin = Admin.query.filter_by(telegram_id=str(user.username)).first()
    
    if not admin:
        await update.message.reply_text("У вас нет доступа к административной панели.")
        return
    
    keyboard = []
    
    # Кнопки доступные всем администраторам
    if admin.can_view_stats():
        keyboard.append([InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")])
    if admin.can_manage_users():
        keyboard.append([InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")])
    if admin.can_manage_orders():
        keyboard.append([InlineKeyboardButton("📦 Управление заказами", callback_data="admin_orders")])
    
    # Кнопки только для superadmin
    if admin.can_manage_admins():
        keyboard.append([InlineKeyboardButton("👑 Управление администраторами", callback_data="admin_manage")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Добро пожаловать в панель администратора, {user.first_name}!\n"
        f"Ваша роль: {admin.role}",
        reply_markup=reply_markup
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки админ-панели"""
    query = update.callback_query
    user = query.from_user
    admin = Admin.query.filter_by(telegram_id=str(user.username)).first()
    
    if not admin:
        await query.answer("У вас нет доступа к этой функции")
        return
    
    action = query.data
    
    if action == "admin_manage" and admin.can_manage_admins():
        # Показываем список администраторов и опции управления
        admins = Admin.query.all()
        text = "👑 Список администраторов:\n\n"
        for a in admins:
            text += f"• {a.username} ({a.role})\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить администратора", callback_data="admin_add")],
            [InlineKeyboardButton("➖ Удалить администратора", callback_data="admin_remove")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "admin_stats":
        # Показываем статистику
        text = "📊 Статистика:\n\n"
        text += "Функция в разработке"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "admin_users":
        # Показываем управление пользователями
        text = "👥 Управление пользователями:\n\n"
        text += "Функция в разработке"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "admin_orders":
        # Показываем управление заказами
        text = "📦 Управление заказами:\n\n"
        text += "Функция в разработке"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif action == "admin_back":
        # Возвращаемся в главное меню админки
        await admin_command(update, context)
    
    await query.answer()

def setup_admin_handlers(application):
    """Регистрация обработчиков админ-команд"""
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_")) 