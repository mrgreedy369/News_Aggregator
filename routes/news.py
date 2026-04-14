from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from models.favourite import Favourite
import requests
import os
from datetime import datetime

news_bp = Blueprint('news', __name__)

NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
NEWS_API_BASE = 'https://newsapi.org/v2'

INDIAN_STATES = [
    'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal',
    'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Kerala', 'Punjab',
    'Telangana', 'Andhra Pradesh', 'Bihar', 'Madhya Pradesh', 'Odisha'
]


def fetch_news(query=None, category=None, country=None, language='en', page_size=12):
    """Fetch news from NewsAPI with fallback"""
    if not NEWS_API_KEY or NEWS_API_KEY == 'your_newsapi_key_here':
        print("⚠️  No valid NEWS_API_KEY found. Using fallback news.")
        return get_fallback_news(category)

    try:
        if query:
            endpoint = f"{NEWS_API_BASE}/everything"
            params = {
                'q': query,
                'language': language,
                'pageSize': page_size,
                'sortBy': 'publishedAt',
                'apiKey': NEWS_API_KEY
            }
        else:
            endpoint = f"{NEWS_API_BASE}/top-headlines"
            params = {
                'language': language,
                'pageSize': page_size,
                'apiKey': NEWS_API_KEY
            }
            if category:
                params['category'] = category
            if country:
                params['country'] = country

        response = requests.get(endpoint, params=params, timeout=10)
        data = response.json()

        if data.get('status') == 'ok':
            articles = []
            for article in data.get('articles', []):
                title = article.get('title', '')
                if title and title != '[Removed]' and article.get('url'):
                    articles.append({
                        'title': title,
                        'description': article.get('description') or 'No description available.',
                        'url': article.get('url', ''),
                        'image_url': article.get('urlToImage') or '',
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'category': category or 'general',
                        'is_favourite': False
                    })
            return articles if articles else get_fallback_news(category)

        print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        return get_fallback_news(category)

    except requests.exceptions.ConnectionError:
        print("❌ No internet connection. Using fallback news.")
        return get_fallback_news(category)
    except requests.exceptions.Timeout:
        print("❌ NewsAPI request timed out. Using fallback news.")
        return get_fallback_news(category)
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return get_fallback_news(category)


def get_fallback_news(category='general'):
    """Return sample news when API is unavailable"""
    news_items = [
        {
            'title': 'Global Leaders Meet to Discuss Climate Change Solutions',
            'description': 'World leaders gather at an international summit to discuss urgent measures needed to combat climate change and reduce carbon emissions globally.',
            'url': 'https://www.bbc.com/news/science-environment',
            'image_url': 'https://picsum.photos/seed/climate/800/400',
            'source': 'BBC News',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'general',
            'is_favourite': False
        },
        {
            'title': 'Technology Giants Announce Major AI Breakthrough',
            'description': 'Leading technology companies have announced a revolutionary artificial intelligence system capable of solving complex scientific problems.',
            'url': 'https://techcrunch.com',
            'image_url': 'https://picsum.photos/seed/tech/800/400',
            'source': 'TechCrunch',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'technology',
            'is_favourite': False
        },
        {
            'title': 'Economic Growth Surges in Emerging Markets',
            'description': 'Emerging market economies show strong growth signals as foreign investments increase and consumer spending rebounds post-pandemic.',
            'url': 'https://www.reuters.com/business',
            'image_url': 'https://picsum.photos/seed/economy/800/400',
            'source': 'Reuters',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'business',
            'is_favourite': False
        },
        {
            'title': 'Scientists Discover New Species in Amazon Rainforest',
            'description': 'A team of international scientists has discovered several previously unknown species of plants and animals in the Amazon rainforest.',
            'url': 'https://www.nationalgeographic.com',
            'image_url': 'https://picsum.photos/seed/science/800/400',
            'source': 'National Geographic',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'science',
            'is_favourite': False
        },
        {
            'title': 'Record-Breaking Performance at World Athletics Championship',
            'description': 'Athletes from around the world deliver stunning performances, breaking multiple world records at the championship held this weekend.',
            'url': 'https://www.espn.com',
            'image_url': 'https://picsum.photos/seed/sports/800/400',
            'source': 'ESPN',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'sports',
            'is_favourite': False
        },
        {
            'title': 'New Healthcare Policy to Improve Access for Millions',
            'description': 'Government announces comprehensive healthcare reform package aimed at improving medical access and reducing costs for citizens.',
            'url': 'https://www.healthline.com',
            'image_url': 'https://picsum.photos/seed/health/800/400',
            'source': 'Healthline',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'health',
            'is_favourite': False
        },
        {
            'title': 'Renewable Energy Investments Hit Record High',
            'description': 'Global investments in renewable energy sources reach an all-time high as countries accelerate transition away from fossil fuels.',
            'url': 'https://www.bloomberg.com/green',
            'image_url': 'https://picsum.photos/seed/energy/800/400',
            'source': 'Bloomberg',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'general',
            'is_favourite': False
        },
        {
            'title': 'Space Agency Announces Plans for Mars Mission',
            'description': 'International space agencies reveal detailed plans for a crewed mission to Mars, targeting launch within the next decade.',
            'url': 'https://www.nasa.gov',
            'image_url': 'https://picsum.photos/seed/space/800/400',
            'source': 'NASA',
            'published_at': datetime.utcnow().isoformat(),
            'category': category or 'science',
            'is_favourite': False
        },
    ]
    return news_items


def mark_favourites(articles, user_id):
    """Mark articles that are in user's favourites"""
    try:
        favourites = Favourite.get_user_favourites(user_id)
        fav_urls = {f['url'] for f in favourites}
        for article in articles:
            article['is_favourite'] = article.get('url', '') in fav_urls
    except Exception as e:
        print(f"Error marking favourites: {e}")
    return articles


@news_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('news.dashboard'))
    return render_template('index.html')


@news_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html',
        states=INDIAN_STATES,
        user=current_user,
        now=datetime.now()
    )


@news_bp.route('/api/news/international')
@login_required
def get_international_news():
    """Fetch top international news"""
    articles = fetch_news(category='general', page_size=8)
    articles = mark_favourites(articles, current_user.id)
    return jsonify({'success': True, 'articles': articles})


@news_bp.route('/api/news/national')
@login_required
def get_national_news():
    """Fetch Indian national news"""
    # Try country-based first, fallback to query
    articles = fetch_news(country='in', page_size=8)
    if not articles:
        articles = fetch_news(query='India news today', page_size=8)
    articles = mark_favourites(articles, current_user.id)
    return jsonify({'success': True, 'articles': articles})


@news_bp.route('/api/news/state/<state_name>')
@login_required
def get_state_news(state_name):
    """Fetch news for a specific Indian state"""
    if state_name not in INDIAN_STATES:
        return jsonify({'success': False, 'message': 'Invalid state name'}), 400

    articles = fetch_news(query=f'{state_name} India news latest', page_size=8)
    articles = mark_favourites(articles, current_user.id)
    return jsonify({'success': True, 'articles': articles, 'state': state_name})


@news_bp.route('/api/news/search')
@login_required
def search_news():
    """Search news by keyword"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'success': False, 'message': 'Search query is required'}), 400

    articles = fetch_news(query=query, page_size=12)
    articles = mark_favourites(articles, current_user.id)
    return jsonify({'success': True, 'articles': articles, 'query': query})


@news_bp.route('/about')
def about():
    return render_template('about.html')