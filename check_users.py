from app import app
from models import User

with app.app_context():
    users = User.query.all()

    for user in users:
        print(user.id, user.username)