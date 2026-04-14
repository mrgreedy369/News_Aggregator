from flask_login import UserMixin
from flask import current_app
from bson import ObjectId
from datetime import datetime


def get_mongo():
    """Get mongo instance from current app context"""
    from app import mongo
    return mongo


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.full_name = user_data.get('full_name', '')
        self.bio = user_data.get('bio', '')
        self.profile_image = user_data.get('profile_image', 'default.png')
        self.location = user_data.get('location', '')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.password_hash = user_data.get('password', '')

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            mongo = get_mongo()
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
        return None

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        try:
            mongo = get_mongo()
            user_data = mongo.db.users.find_one({'email': email})
            if user_data:
                return User(user_data)
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
        return None

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        try:
            mongo = get_mongo()
            user_data = mongo.db.users.find_one({'username': username})
            if user_data:
                return User(user_data)
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
        return None

    @staticmethod
    def create(bcrypt, username, email, password, full_name=''):
        """Create a new user"""
        try:
            mongo = get_mongo()
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user_data = {
                'username': username,
                'email': email,
                'password': password_hash,
                'full_name': full_name,
                'bio': '',
                'location': '',
                'profile_image': 'default.png',
                'created_at': datetime.utcnow()
            }
            result = mongo.db.users.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            return User(user_data)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def update(user_id, update_data):
        """Update user data"""
        try:
            mongo = get_mongo()
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def check_password(self, bcrypt, password):
        """Verify password"""
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except Exception as e:
            print(f"Error checking password: {e}")
            return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'location': self.location,
            'created_at': self.created_at
        }