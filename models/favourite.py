from datetime import datetime
from bson import ObjectId


def get_mongo():
    """Get mongo instance from app context"""
    from app import mongo
    return mongo


class Favourite:

    @staticmethod
    def add(user_id, article):
        """Add article to user's favourites"""
        try:
            mongo = get_mongo()

            # Check if already exists
            existing = mongo.db.favourites.find_one({
                'user_id': user_id,
                'url': article.get('url', '')
            })
            if existing:
                return {'success': False, 'message': 'Already saved to favourites'}

            favourite_data = {
                'user_id': user_id,
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'image_url': article.get('image_url', ''),
                'source': article.get('source', ''),
                'category': article.get('category', 'general'),
                'saved_at': datetime.utcnow()
            }
            mongo.db.favourites.insert_one(favourite_data)
            return {'success': True, 'message': 'Article saved to favourites'}

        except Exception as e:
            print(f"Error adding favourite: {e}")
            return {'success': False, 'message': 'Error saving article'}

    @staticmethod
    def remove(user_id, article_url):
        """Remove article from user's favourites"""
        try:
            mongo = get_mongo()
            result = mongo.db.favourites.delete_one({
                'user_id': user_id,
                'url': article_url
            })
            if result.deleted_count > 0:
                return {'success': True, 'message': 'Removed from favourites'}
            return {'success': False, 'message': 'Article not found in favourites'}
        except Exception as e:
            print(f"Error removing favourite: {e}")
            return {'success': False, 'message': 'Error removing article'}

    @staticmethod
    def get_user_favourites(user_id):
        """Get all favourites for a user"""
        try:
            mongo = get_mongo()
            favourites = list(mongo.db.favourites.find(
                {'user_id': user_id}
            ).sort('saved_at', -1))

            # Convert ObjectId to string
            for fav in favourites:
                fav['_id'] = str(fav['_id'])

            return favourites
        except Exception as e:
            print(f"Error getting favourites: {e}")
            return []

    @staticmethod
    def is_favourite(user_id, article_url):
        """Check if article is in user's favourites"""
        try:
            mongo = get_mongo()
            existing = mongo.db.favourites.find_one({
                'user_id': user_id,
                'url': article_url
            })
            return existing is not None
        except Exception as e:
            print(f"Error checking favourite: {e}")
            return False

    @staticmethod
    def count_user_favourites(user_id):
        """Count favourites for a user"""
        try:
            mongo = get_mongo()
            return mongo.db.favourites.count_documents({'user_id': user_id})
        except Exception as e:
            print(f"Error counting favourites: {e}")
            return 0