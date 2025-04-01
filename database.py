from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String)
    stock = Column(Integer, default=0)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    cart = relationship("CartItem", back_populates="user")

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    
    user = relationship("User", back_populates="cart")
    product = relationship("Product")

# Создаем приложение Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'shop': 'sqlite:///shop.db'
}

# Инициализируем SQLAlchemy
db = SQLAlchemy(app)

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        from models.admin import Admin
        Admin.init_superadmin()

def get_session():
    return Session()

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all() 