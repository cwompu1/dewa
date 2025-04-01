from app import app, db
from models.admin import Admin
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        
        # Проверяем, существует ли уже администратор
        admin = Admin.query.filter_by(username=os.getenv('ADMIN_USERNAME')).first()
        
        if not admin:
            # Создаем нового администратора
            admin = Admin(
                username=os.getenv('ADMIN_USERNAME'),
                password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD'))
            )
            db.session.add(admin)
            db.session.commit()
            print('Администратор успешно создан!')
        else:
            print('Администратор уже существует!')

if __name__ == '__main__':
    init_db() 