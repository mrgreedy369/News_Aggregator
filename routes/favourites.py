from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.favourite import Favourite

favourites_bp = Blueprint('favourites', __name__)


@favourites_bp.route('/')
@login_required
def saved_news():
    favourites = Favourite.get_user_favourites(current_user.id)
    return render_template(
        'saved_news.html',
        favourites=favourites,
        user=current_user
    )


@favourites_bp.route('/add', methods=['POST'])
@login_required
def add_favourite():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    article = {
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'url': data.get('url', ''),
        'image_url': data.get('image_url', ''),
        'source': data.get('source', ''),
        'category': data.get('category', 'general')
    }

    if not article['url']:
        return jsonify({'success': False, 'message': 'Article URL is required'}), 400

    result = Favourite.add(current_user.id, article)
    return jsonify(result)


@favourites_bp.route('/remove', methods=['POST'])
@login_required
def remove_favourite():
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({'success': False, 'message': 'Article URL is required'}), 400

    result = Favourite.remove(current_user.id, data['url'])
    return jsonify(result)


@favourites_bp.route('/check', methods=['POST'])
@login_required
def check_favourite():
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({'is_favourite': False})

    is_fav = Favourite.is_favourite(current_user.id, data['url'])
    return jsonify({'is_favourite': is_fav})