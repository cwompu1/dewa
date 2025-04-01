from database import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(200))
    tracking_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, total_amount, shipping_address=None):
        self.user_id = user_id
        self.total_amount = total_amount
        self.shipping_address = shipping_address
    
    def update_status(self, new_status):
        """Обновить статус заказа"""
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_tracking(self, tracking_number):
        """Добавить номер отслеживания"""
        self.tracking_number = tracking_number
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_user_orders(user_id):
        """Получить все заказы пользователя"""
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_orders_by_status(status):
        """Получить все заказы с определенным статусом"""
        return Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all() 