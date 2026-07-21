from flask import Flask
from werkzeug.security import generate_password_hash,check_password_hash;
from application.database import db
from application.models import User

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'placement-secret-key'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bytrek.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    return app

app = create_app()

db.init_app(app)

from application.controller import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        manager = User.query.filter_by(email="admin@gmail.com").first()
        if manager is None:
            
            hash_pass = generate_password_hash("admin123")
            manager = User(email="admin@gmail.com", password=hash_pass,role="admin")
            db.session.add(manager)
            db.session.commit()

    app.run(debug=True)