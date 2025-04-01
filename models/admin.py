from database import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')  # superadmin, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    
    # Отношения
    created_admins = db.relationship('Admin', backref=db.backref('creator', remote_side=[id]))
    
    def __init__(self, telegram_id, username, role='admin', created_by=None):
        self.telegram_id = telegram_id
        self.username = username
        self.role = role
        self.created_by = created_by
    
    @staticmethod
    def init_superadmin():
        """Инициализация главного администратора"""
        try:
            superadmin = Admin.query.filter_by(role='superadmin').first()
            if not superadmin:
                superadmin = Admin(
                    telegram_id=7829321327,  # Your actual Telegram ID
                    username='cwompubot',  # Your bot's username
                    role='superadmin'
                )
                db.session.add(superadmin)
                db.session.commit()
            return superadmin
        except Exception as e:
            print(f"Error initializing superadmin: {e}")
            db.session.rollback()
            return None
    
    def can_manage_admins(self):
        """Проверка прав на управление администраторами"""
        return self.role == 'superadmin'
    
    def can_view_stats(self):
        """Проверка прав на просмотр статистики"""
        return True
    
    def can_manage_users(self):
        """Проверка прав на управление пользователями"""
        return True
    
    def can_manage_orders(self):
        """Проверка прав на управление заказами"""
        return True 