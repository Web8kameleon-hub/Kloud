#!/usr/bin/env python3
"""
LinkedIn Auto Poster - Automated content publishing system
Posts blog articles to LinkedIn on a schedule

Features:
- Daily cron job posting
- Tracks posted articles to avoid duplicates
- Generates engaging post text from article content
- Supports manual posting via API
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('linkedin_auto_poster')

# Configuration
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN', 'urn:li:person:5KOBp94BOT')
POSTED_ARTICLES_FILE = Path('/app/data/posted_articles.json')
BLOG_URL = os.getenv('BLOG_URL', 'https://ledjanahmati.github.io/kloud-blog/')
SITE_URL = os.getenv('SITE_URL', 'https://kloud.com')

# Ensure data directory exists
POSTED_ARTICLES_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_posted_articles() -> set:
    """Load the set of already posted article IDs."""
    if POSTED_ARTICLES_FILE.exists():
        try:
            with open(POSTED_ARTICLES_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('posted', []))
        except Exception as e:
            logger.error(f"Error loading posted articles: {e}")
    return set()


def save_posted_article(article_id: str) -> None:
    """Save an article ID to the posted list."""
    posted = load_posted_articles()
    posted.add(article_id)
    
    with open(POSTED_ARTICLES_FILE, 'w') as f:
        json.dump({
            'posted': list(posted),
            'last_updated': datetime.now().isoformat()
        }, f, indent=2)


def generate_post_text(article: dict) -> str:
    """Generate engaging LinkedIn post text from article data."""
    title = article.get('title', 'New Article')
    description = article.get('description', article.get('excerpt', ''))
    # Use direct blog URL if available, otherwise construct from slug
    article_url = article.get('url', f"{BLOG_URL}static/{article.get('slug', '')}.html")
    tags = article.get('tags', [])
    
    # Build hashtags from tags
    hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:5]])
    if not hashtags:
        hashtags = '#AI #CloudComputing #EEG #IndustrialAI #Kloud'
    
    # Generate post text
    post_text = f"""🚀 New Article: {title}

{description[:200]}{'...' if len(description) > 200 else ''}

📖 Read more: {article_url}

{hashtags}

#Kloud #TechInnovation"""
    
    return post_text


def post_to_linkedin(text: str) -> dict:
    """Post content to LinkedIn."""
    if not LINKEDIN_ACCESS_TOKEN:
        logger.error("LINKEDIN_ACCESS_TOKEN not configured")
        return {'success': False, 'error': 'Token not configured'}
    
    headers = {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    post_data = {
        'author': LINKEDIN_PERSON_URN,
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': text
                },
                'shareMediaCategory': 'NONE'
            }
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
    }
    
    try:
        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=post_data,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"Successfully posted to LinkedIn: {result.get('id')}")
            return {'success': True, 'post_id': result.get('id')}
        else:
            logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {e}")
        return {'success': False, 'error': str(e)}


def fetch_blog_articles() -> list:
    """Fetch articles from GitHub Pages blog by parsing HTML."""
    import re
    try:
        response = requests.get(BLOG_URL, timeout=15)
        if response.status_code == 200:
            html = response.text
            # Parse article links from HTML
            # Format: <a href="static/2026-02-07-slug.html">Title</a>
            pattern = r'href="(static/(\d{4}-\d{2}-\d{2})-([^"]+)\.html)">([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            articles = []
            for url_path, date, slug, title in matches:
                # Clean up title
                title = title.strip()
                if not title or title == 'Kloud Blog':
                    continue
                
                full_url = f"{BLOG_URL.rstrip('/')}/{url_path}"
                    
                articles.append({
                    'id': f"{date}-{slug}",
                    'title': title,
                    'description': f'Read our latest article: {title}',
                    'slug': slug,
                    'url': full_url,
                    'date': date,
                    'category': 'Blog',
                    'tags': extract_tags_from_title(title)
                })
            
            logger.info(f"Fetched {len(articles)} articles from blog")
            return articles
    except Exception as e:
        logger.error(f"Error fetching articles from blog: {e}")
    
    # Fallback: return sample articles if blog not available
    return get_sample_articles()


def extract_tags_from_title(title: str) -> list:
    """Extract relevant hashtags from article title."""
    keywords = {
        'EEG': 'EEG', 'Brain': 'BrainTech', 'Neural': 'NeuralNetworks',
        'AI': 'AI', 'Healthcare': 'Healthcare', 'FDA': 'FDA',
        'Edge': 'EdgeComputing', 'Cloud': 'CloudComputing',
        'Medical': 'MedicalDevices', 'Compliance': 'Compliance',
        'Data': 'DataScience', 'Audio': 'AudioAnalysis',
        'Signal': 'SignalProcessing', 'Privacy': 'DataPrivacy',
        'Industrial': 'IndustrialAI', 'Sustainable': 'Sustainability'
    }
    
    tags = ['Kloud']
    for keyword, tag in keywords.items():
        if keyword.lower() in title.lower():
            tags.append(tag)
    
    return tags[:5]  # Limit to 5 tags


def get_sample_articles() -> list:
    """Return sample articles for testing."""
    return [
        {
            'id': 'eeg-analysis-intro',
            'title': 'Introduction to EEG Analysis with AI',
            'description': 'Learn how artificial intelligence is revolutionizing EEG signal processing and brain-computer interfaces.',
            'slug': 'eeg-analysis-intro',
            'category': 'EEG Analytics',
            'tags': ['EEG', 'AI', 'BrainTech', 'NeuralNetworks']
        },
        {
            'id': 'industrial-ai-2026',
            'title': 'Industrial AI Trends for 2026',
            'description': 'Discover the latest trends in industrial artificial intelligence and how they are transforming manufacturing.',
            'slug': 'industrial-ai-trends-2026',
            'category': 'Industrial AI',
            'tags': ['IndustrialAI', 'Manufacturing', 'Industry40', 'Automation']
        },
        {
            'id': 'fda-compliance-ai',
            'title': 'FDA Compliance in AI Medical Devices',
            'description': 'A comprehensive guide to navigating FDA regulations for AI-powered medical devices and software.',
            'slug': 'fda-compliance-ai-medical',
            'category': 'Compliance',
            'tags': ['FDA', 'MedicalDevices', 'Compliance', 'Healthcare']
        },
        {
            'id': 'ocean-ai-launch',
            'title': 'Introducing Curiosity Ocean: Your AI Research Assistant',
            'description': 'Meet Curiosity Ocean, our advanced AI assistant for research, document analysis, and intelligent Q&A.',
            'slug': 'curiosity-ocean-launch',
            'category': 'Product',
            'tags': ['AI', 'ChatBot', 'Research', 'Productivity']
        },
        {
            'id': 'neural-biofeedback',
            'title': 'Real-time Neural Biofeedback Systems',
            'description': 'How real-time biofeedback is enabling new therapeutic approaches for stress, focus, and mental wellness.',
            'slug': 'neural-biofeedback-systems',
            'category': 'EEG Analytics',
            'tags': ['Biofeedback', 'Neuroscience', 'Wellness', 'MentalHealth']
        }
    ]


def run_daily_post() -> dict:
    """Run the daily posting job - posts one unposted article."""
    logger.info("Starting daily LinkedIn post job...")
    
    posted = load_posted_articles()
    articles = fetch_blog_articles()
    
    # Find an article that hasn't been posted yet
    for article in articles:
        article_id = article.get('id') or hashlib.md5(article.get('title', '').encode()).hexdigest()
        
        if article_id not in posted:
            logger.info(f"Found unposted article: {article.get('title')}")
            
            # Generate and post
            post_text = generate_post_text(article)
            result = post_to_linkedin(post_text)
            
            if result.get('success'):
                save_posted_article(article_id)
                return {
                    'success': True,
                    'article': article.get('title'),
                    'post_id': result.get('post_id')
                }
            else:
                return {
                    'success': False,
                    'article': article.get('title'),
                    'error': result.get('error')
                }
    
    logger.info("No new articles to post")
    return {'success': True, 'message': 'No new articles to post'}


def post_specific_article(article_id: str) -> dict:
    """Post a specific article by ID (manual trigger)."""
    articles = fetch_blog_articles()
    
    for article in articles:
        if article.get('id') == article_id or article.get('slug') == article_id:
            post_text = generate_post_text(article)
            result = post_to_linkedin(post_text)
            
            if result.get('success'):
                save_posted_article(article_id)
            
            return result
    
    return {'success': False, 'error': 'Article not found'}


def post_custom_content(text: str) -> dict:
    """Post custom content to LinkedIn (manual)."""
    return post_to_linkedin(text)


# FastAPI endpoints for the automation service
def create_app():
    """Create FastAPI app for the LinkedIn automation service."""
    from fastapi import BackgroundTasks, FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(
        title="LinkedIn Auto Poster",
        description="Automated LinkedIn posting service for Kloud blog articles",
        version="1.0.0"
    )
    
    class CustomPostRequest(BaseModel):
        text: str
    
    class ArticlePostRequest(BaseModel):
        article_id: str
    
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": "linkedin-auto-poster",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.post("/api/linkedin/post-daily")
    async def trigger_daily_post(background_tasks: BackgroundTasks) -> dict[str, object]:
        """Trigger the daily posting job."""
        result = run_daily_post()
        return result
    
    @app.post("/api/linkedin/post-article")
    async def post_article(request: ArticlePostRequest):
        """Post a specific article to LinkedIn."""
        result = post_specific_article(request.article_id)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        return result
    
    @app.post("/api/linkedin/post-custom")
    async def post_custom(request: CustomPostRequest):
        """Post custom content to LinkedIn."""
        result = post_custom_content(request.text)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        return result
    
    @app.get("/api/linkedin/posted-articles")
    async def get_posted_articles():
        """Get list of already posted articles."""
        posted = load_posted_articles()
        return {"posted": list(posted), "count": len(posted)}
    
    @app.get("/api/linkedin/pending-articles")
    async def get_pending_articles():
        """Get list of articles not yet posted."""
        posted = load_posted_articles()
        articles = fetch_blog_articles()
        
        pending = []
        for article in articles:
            article_id = article.get('id') or hashlib.md5(article.get('title', '').encode()).hexdigest()
            if article_id not in posted:
                pending.append(article)
        
        return {"pending": pending, "count": len(pending)}
    
    return app


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "daily":
            # Run daily job
            result = run_daily_post()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "test":
            # Test posting
            result = post_custom_content("🧪 Test post from Kloud LinkedIn Auto Poster!")
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "serve":
            # Run as API server
            import uvicorn
            app = create_app()
            uvicorn.run(app, host="0.0.0.0", port=8007)
    else:
        print("Usage: python linkedin_auto_poster.py [daily|test|serve]")

