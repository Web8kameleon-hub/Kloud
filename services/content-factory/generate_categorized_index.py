#!/usr/bin/env python3
"""
Generate Categorized Blog Index
Fetches articles from GitHub repo and generates a modern categorized index.html
"""

import base64
import json
import os
import re
from pathlib import Path

import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO = "LedjanAhmati/kloud-blog"
BRANCH = "main"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_articles_from_static():
    """Fetch list of HTML articles from static/ folder"""
    url = f"https://api.github.com/repos/{REPO}/contents/static"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"Error fetching static folder: {resp.status_code}")
        return []
    
    files = resp.json()
    articles = []
    
    for f in files:
        if f['name'].endswith('.html'):
            # Parse filename for date and title
            # Format: YYYY-MM-DD-title-with-dashes.html
            filename = f['name']
            match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.html', filename)
            
            if match:
                date_str = match.group(1)
                title_slug = match.group(2)
                # Convert slug to title
                title = title_slug.replace('-', ' ').title()
                
                articles.append({
                    'filename': filename,
                    'title': title,
                    'date': date_str,
                    'author': 'Kloud'
                })
            else:
                # Fallback for non-standard filenames
                articles.append({
                    'filename': filename,
                    'title': filename.replace('.html', '').replace('-', ' ').title(),
                    'date': '2025-01-01',
                    'author': 'Kloud'
                })
    
    # Sort by date descending
    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles

def fetch_articles_from_posts():
    """Fetch list of markdown posts from _posts/ folder"""
    url = f"https://api.github.com/repos/{REPO}/contents/_posts"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"Error fetching _posts folder: {resp.status_code}")
        return []
    
    files = resp.json()
    articles = []
    
    for f in files:
        if f['name'].endswith('.md'):
            filename = f['name']
            match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', filename)
            
            if match:
                date_str = match.group(1)
                title_slug = match.group(2)
                title = title_slug.replace('-', ' ').title()
                
                # Link to static HTML version
                html_filename = filename.replace('.md', '.html')
                
                articles.append({
                    'filename': html_filename,
                    'title': title,
                    'date': date_str,
                    'author': 'Kloud'
                })
    
    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles

def generate_index_html(articles):
    """Generate index.html with categorized articles"""
    
    # Load template
    template_path = Path(__file__).parent / "blog_index_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Convert articles to JSON
    articles_json = json.dumps(articles, ensure_ascii=False, indent=2)
    
    # Replace placeholder
    html = template.replace('__ARTICLES_DATA__', articles_json)
    
    return html

def upload_to_github(content: str, path: str, message: str):
    """Upload file to GitHub repo"""
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    
    # Get current file SHA if exists
    resp = requests.get(url, headers=headers)
    sha = None
    if resp.status_code == 200:
        sha = resp.json().get('sha')
    
    # Encode content
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    data = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    
    if sha:
        data["sha"] = sha
    
    resp = requests.put(url, headers=headers, json=data)
    
    if resp.status_code in [200, 201]:
        print(f"✅ Successfully uploaded {path}")
        return True
    else:
        print(f"❌ Failed to upload {path}: {resp.status_code}")
        print(resp.json())
        return False

def main():
    print("📚 Fetching articles from GitHub...")
    
    # Try static folder first (contains HTML files)
    articles = fetch_articles_from_static()
    
    if not articles:
        print("No articles in static/, trying _posts/...")
        articles = fetch_articles_from_posts()
    
    print(f"📊 Found {len(articles)} articles")
    
    if not articles:
        print("❌ No articles found!")
        return
    
    # Show category breakdown
    categories = {}
    for a in articles:
        title_lower = a['title'].lower()
        if 'eeg' in title_lower or 'brain' in title_lower or 'neural' in title_lower:
            cat = 'eeg'
        elif 'audio' in title_lower or 'speech' in title_lower:
            cat = 'audio'
        elif 'cardiac' in title_lower or 'hormon' in title_lower or 'medical' in title_lower or 'clinical' in title_lower:
            cat = 'medical'
        elif 'compliance' in title_lower or 'gdpr' in title_lower or 'fda' in title_lower:
            cat = 'compliance'
        elif 'industrial' in title_lower or 'factory' in title_lower:
            cat = 'industrial'
        else:
            cat = 'ai'
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Category Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    print("\n🔨 Generating categorized index.html...")
    html = generate_index_html(articles)
    
    print(f"📄 Generated HTML: {len(html)} bytes")
    
    print("\n🚀 Uploading to GitHub...")
    success = upload_to_github(
        html, 
        "index.html", 
        f"🎨 Update: Categorized blog UI with {len(articles)} articles"
    )
    
    if success:
        print("\n✅ Blog updated successfully!")
        print(f"🔗 Visit: https://ledjanahmati.github.io/kloud-blog/")
    else:
        print("\n❌ Failed to update blog")

if __name__ == "__main__":
    main()

