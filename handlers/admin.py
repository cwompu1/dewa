from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from models.admin import Admin
from database import db, app
import logging

logger = logging.getLogger(__name__)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin"""
    try:
        user = update.effective_user
        logger.info(f"Admin command received from user {user.username}")
        
        # Проверяем, является ли пользователь администратором
        with app.app_context():
            admin = Admin.query.filter_by(username=user.username).first()
            
            if not admin:
                logger.warning(f"Unauthorized access attempt from user {user.username}")
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
            logger.info(f"Admin panel shown to user {user.username}")
        
    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки админ-панели"""
    try:
        query = update.callback_query
        user = query.from_user
        
        with app.app_context():
            # Проверяем права доступа
            admin = Admin.query.filter_by(username=user.username).first()
            if not admin:
                await query.answer("У вас нет доступа к этой функции")
                return
            
            action = query.data
            logger.info(f"Admin action {action} requested by user {user.username}")
            
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
                from models.user import User
                from models.order import Order
                
                users_count = User.query.count()
                orders_count = Order.query.count()
                total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
                
                text = "📊 Статистика магазина:\n\n"
                text += f"👥 Пользователей: {users_count}\n"
                text += f"📦 Заказов: {orders_count}\n"
                text += f"💰 Общая выручка: {total_revenue:,.2f} ₽\n\n"
                
                # Статистика за последние 7 дней
                from datetime import datetime, timedelta
                week_ago = datetime.utcnow() - timedelta(days=7)
                new_users = User.query.filter(User.created_at >= week_ago).count()
                new_orders = Order.query.filter(Order.created_at >= week_ago).count()
                
                text += "За последние 7 дней:\n"
                text += f"👥 Новых пользователей: {new_users}\n"
                text += f"📦 Новых заказов: {new_orders}"
                
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                
            elif action == "admin_users":
                # Показываем управление пользователями
                from models.user import User
                
                # Получаем последних 5 пользователей
                recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
                
                text = "👥 Управление пользователями:\n\n"
                text += "Последние пользователи:\n"
                for user in recent_users:
                    text += f"• {user.username} (ID: {user.telegram_id})\n"
                    text += f"  Регистрация: {user.created_at.strftime('%d.%m.%Y')}\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔍 Поиск пользователя", callback_data="user_search")],
                    [InlineKeyboardButton("📊 Подробная статистика", callback_data="user_stats")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
                ]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                
            elif action == "admin_orders":
                # Показываем управление заказами
                from models.order import Order
                
                # Получаем последние 5 заказов
                recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
                
                text = "📦 Управление заказами:\n\n"
                text += "Последние заказы:\n"
                for order in recent_orders:
                    text += f"• Заказ #{order.id}\n"
                    text += f"  Статус: {order.status}\n"
                    text += f"  Сумма: {order.total_amount:,.2f} ₽\n"
                    text += f"  Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔍 Поиск заказа", callback_data="order_search")],
                    [InlineKeyboardButton("📊 Статистика заказов", callback_data="order_stats")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
                ]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                
            elif action == "admin_back":
                # Возвращаемся в главное меню админки
                await admin_command(update, context)
            
            await query.answer()
            logger.info(f"Admin action {action} completed for user {user.username}")
        
    except Exception as e:
        logger.error(f"Error in admin callback: {e}")
        await query.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

def setup_admin_handlers(application):
    """Регистрация обработчиков админ-команд"""
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    logger.info("Admin handlers registered successfully") 