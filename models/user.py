from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def __init__(self, telegram_id, username=None, first_name=None, last_name=None):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
    
    @property
    def full_name(self):
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or str(self.telegram_id)
    
    def get_orders_count(self):
        """Получить количество заказов пользователя"""
        return len(self.orders)
    
    def get_total_spent(self):
        """Получить общую сумму заказов пользователя"""
        return sum(order.total_amount for order in self.orders if order.status == 'completed')
    
    @staticmethod
    def get_or_create(telegram_id, username=None, first_name=None, last_name=None):
        """Получить существующего пользователя или создать нового"""
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.session.add(user)
            db.session.commit()
        return user 