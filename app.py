from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import os

# Initialize extensions (without app)
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions WITH app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Test MongoDB connection
    with app.app_context():
        try:
            mongo.db.command('ping')
            print("✅ MongoDB connected successfully!")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("Make sure MongoDB is running on your system.")

    # Register blueprints INSIDE app context
    from routes.auth import auth_bp
    from routes.news import news_bp
    from routes.profile import profile_bp
    from routes.favourites import favourites_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(news_bp, url_prefix='/')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(favourites_bp, url_prefix='/favourites')

    # User loader
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    return app


# Create app instance at module level for imports
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)