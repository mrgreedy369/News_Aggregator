import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    MONGO_URI = os.environ.get(
        'MONGO_URI'
    )

    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static', 'uploads', 'profiles'
    )

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    NEWS_API_BASE_URL = 'https://newsapi.org/'