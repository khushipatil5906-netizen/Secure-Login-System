from flask import Flask, render_template, request, redirect, flash
from models import db, User
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Route
@app.route('/')
def home():
    return redirect('/login')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username'].strip()
        password = request.form['password']

        # Validation
        if len(username) < 3:
            flash("Username must be at least 3 characters")
            return redirect('/register')

        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect('/register')

        # Check Existing User
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Username already exists")
            return redirect('/register')

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        # Create User
        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")
        return redirect('/login')

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
                user.password,
                password):

            login_user(user)

            return redirect('/dashboard')

        flash("Invalid Username or Password")

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html',
        name=current_user.username
    )


# Logout
@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect('/login')


# Run App
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)