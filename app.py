from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import db
from models.admin import Admin
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///admin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('index'))
        flash('Неверные учетные данные')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/stats')
@login_required
def get_stats():
    from models.user import User
    from models.order import Order
    
    users_count = User.query.count()
    orders_count = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    return jsonify({
        'users_count': users_count,
        'orders_count': orders_count,
        'total_revenue': total_revenue
    })

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Debug mode: ON")
    print("Access URLs:")
    print("------------------------------------------------")
    print("Local: http://127.0.0.1:8080")
    print("External: http://0.0.0.0:8080")
    print("------------------------------------------------")
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 