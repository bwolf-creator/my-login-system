from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bwolf-super-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create database and test user
with app.app_context():
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin123")
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created: admin / admin123")

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr
    
    if not username or not password:
        return render_template('login.html', error="Please enter both fields")
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.password_hash == hash_password(password):
        # Successful login
        print("="*50)
        print(f"✅✅✅ SUCCESSFUL LOGIN!")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"🌐 IP: {ip}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        session['username'] = username
        return render_template('dashboard.html', username=username)
    else:
        # Failed login
        print(f"❌ FAILED LOGIN: {username} | {password} from {ip}")
        return render_template('login.html', error="Invalid username or password")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
