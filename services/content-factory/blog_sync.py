"""
KLOUD BLOG SYNC - "Batica-Zbatica" Content Flow
===================================================

Syncs auto-generated content from Content Factory to separate GitHub Pages repository.

Flow: Kloud-cloud (engine) → kloud-blog (public website)

This keeps the main repo clean while publishing content to the world.

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("blog_sync")


class BlogSync:
    """
    Syncs generated content to a separate GitHub Pages repository.
    
    Architecture (Batica-Zbatica):
    - Main repo: Kloud-cloud (private, engine code)
    - Blog repo: kloud-blog (public, GitHub Pages)
    - Content flows OUT from main to blog on schedule or trigger
    """
    
    def __init__(
        self,
        source_dir: str = "/app/published",
        blog_repo_url: Optional[str] = None,
        blog_dir: str = "/app/blog-repo",
        github_token: Optional[str] = None
    ):
        self.source_dir = Path(source_dir)
        self.blog_dir = Path(blog_dir)
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        
        # Blog repo URL - can use token for auth
        self.blog_repo_url = blog_repo_url or os.environ.get(
            "BLOG_REPO_URL",
            "https://github.com/LedjanAhmati/kloud-blog.git"
        )
        
        self._initialized = False
        self._stats: Dict[str, Any] = {
            "total_synced": 0,
            "last_sync": None,
            "errors": []
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize or clone the blog repository"""
        try:
            if self.blog_dir.exists() and (self.blog_dir / ".git").exists():
                # Pull latest
                result = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=self.blog_dir,
                    capture_output=True,
                    text=True
                )
                self._initialized = True
                return {"status": "updated", "message": "Pulled latest from blog repo"}
            
            # Clone the repo
            self.blog_dir.mkdir(parents=True, exist_ok=True)
            
            # Use token in URL for auth if available
            clone_url = self.blog_repo_url
            if clone_url is None:
                # No repo URL configured, create local
                subprocess.run(["git", "init"], cwd=self.blog_dir, check=True)
                self._create_jekyll_structure()
                return {"status": "created", "message": "Created new blog repo locally (no remote configured)"}
            
            if self.github_token and "github.com" in clone_url:
                clone_url = clone_url.replace(
                    "https://github.com",
                    f"https://{self.github_token}@github.com"
                )
            
            result = subprocess.run(
                ["git", "clone", clone_url, str(self.blog_dir)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Repo doesn't exist yet, create local
                subprocess.run(["git", "init"], cwd=self.blog_dir, check=True)
                self._create_jekyll_structure()
                return {"status": "created", "message": "Created new blog repo locally"}
            
            self._initialized = True
            return {"status": "cloned", "message": "Cloned blog repo"}
            
        except Exception as e:
            logger.error(f"Failed to initialize blog repo: {e}")
            return {"status": "error", "error": str(e)}
    
    def _create_jekyll_structure(self) -> None:
        """Create basic Jekyll structure for GitHub Pages"""
        # _config.yml
        config = """
title: Kloud Blog
description: Advancing Healthcare Through Intelligent Signal Processing
author: Kloud AI
url: https://ledjanahmat.github.io
baseurl: /kloud-blog

# Build settings
markdown: kramdown
theme: minima

# Plugins
plugins:
  - jekyll-feed
  - jekyll-seo-tag

# Collections
collections:
  posts:
    output: true
    permalink: /blog/:year/:month/:day/:title/

# Social
github_username: LedjanAhmati
twitter_username: kloud

# Analytics (optional)
# google_analytics: UA-XXXXXXXX-X
"""
        (self.blog_dir / "_config.yml").write_text(config.strip())
        
        # Create directories
        (self.blog_dir / "_posts").mkdir(exist_ok=True)
        (self.blog_dir / "_layouts").mkdir(exist_ok=True)
        (self.blog_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
        
        # index.html
        index_html = """---
layout: default
title: Home
---

<div class="posts">
{% for post in site.posts limit:10 %}
  <article class="post-preview">
    <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
    <time>{{ post.date | date: "%B %d, %Y" }}</time>
    <p>{{ post.excerpt | strip_html | truncatewords: 50 }}</p>
  </article>
{% endfor %}
</div>
"""
        (self.blog_dir / "index.html").write_text(index_html)
        
        # README.md
        readme = """# Kloud Blog

Auto-generated content from Kloud AI Content Factory.

🏥 **Advancing Healthcare Through Intelligent Signal Processing**

## Topics

- EEG & Neuroscience
- Audio Processing
- AI/ML Systems  
- Healthcare Technology
- Regulatory Compliance
- Enterprise AI

## About

This blog is automatically generated by the Kloud Content Factory.
New articles are published daily covering topics in healthcare technology and AI.

---

© 2026 Kloud - ABA GmbH
"""
        (self.blog_dir / "README.md").write_text(readme)
        
        logger.info("Created Jekyll blog structure")
    
    def _regenerate_index(self) -> None:
        """Regenerate index.html with all current articles"""
        static_dir = self.blog_dir / "static"
        if not static_dir.exists():
            return
        
        # Get all HTML articles sorted by date (newest first)
        articles = sorted(static_dir.glob("*.html"), reverse=True)
        
        # Generate article list HTML
        article_items = []
        for article in articles:
            # Parse filename: 2026-02-06-title-here.html
            name = article.stem
            parts = name.split("-", 3)
            if len(parts) >= 4:
                title_slug = parts[3]
                # Convert slug to title
                title = title_slug.replace("-", " ").title()
                if len(title) > 60:
                    title = title[:57] + "..."
                date_display = f"{parts[1]}/{parts[2]}/{parts[0]}"
            else:
                title = name.replace("-", " ").title()
                date_display = "Recent"
            
            article_items.append(
                f'            <article><h2><a href="static/{article.name}">{title}</a></h2>'
                f'<span class="date">{date_display}</span></article>'
            )
        
        articles_html = "\n".join(article_items)
        
        index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kloud Blog - AI & Industrial Intelligence</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 100%); color: #e0e0e0; min-height: 100vh; }}
        header {{ background: rgba(0,0,0,0.3); padding: 2rem; text-align: center; border-bottom: 1px solid #333; }}
        header h1 {{ font-size: 2.5rem; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        header p {{ color: #888; margin-top: 0.5rem; }}
        .count {{ color: #00d4ff; font-size: 0.9rem; margin-top: 1rem; }}
        main {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        .articles {{ display: grid; gap: 1.5rem; }}
        article {{ background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 12px; padding: 1.5rem; transition: all 0.3s; }}
        article:hover {{ border-color: #00d4ff; transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,212,255,0.1); }}
        article h2 {{ font-size: 1.2rem; margin-bottom: 0.5rem; }}
        article h2 a {{ color: #00d4ff; text-decoration: none; }}
        article h2 a:hover {{ text-decoration: underline; }}
        article .date {{ color: #666; font-size: 0.85rem; }}
        footer {{ text-align: center; padding: 2rem; color: #555; border-top: 1px solid #333; margin-top: 3rem; }}
    </style>
</head>
<body>
    <header>
        <h1>Kloud Blog</h1>
        <p>AI, EEG Analytics, Industrial Intelligence & Compliance</p>
        <p class="count">{len(articles)} Articles</p>
    </header>
    <main>
        <div class="articles">
{articles_html}
        </div>
    </main>
    <footer>
        <p>&copy; 2026 Kloud - Powered by AI</p>
    </footer>
</body>
</html>'''
        
        (self.blog_dir / "index.html").write_text(index_html)
        logger.info(f"Regenerated index.html with {len(articles)} articles")

    async def sync(self, push: bool = True) -> Dict[str, Any]:
        """
        Sync content from source to blog repo (Batica-Zbatica flow)
        
        Args:
            push: Whether to push to remote after sync
        """
        if not self._initialized:
            init_result = await self.initialize()
            if init_result.get("status") == "error":
                return init_result
        
        results: Dict[str, Any] = {
            "synced_files": [],
            "skipped_files": [],
            "errors": [],
            "pushed": False
        }
        
        try:
            # Sync Jekyll posts
            source_posts = self.source_dir / "blog" / "_posts"
            target_posts = self.blog_dir / "_posts"
            target_posts.mkdir(exist_ok=True)
            
            if source_posts.exists():
                for post_file in source_posts.glob("*.md"):
                    target_file = target_posts / post_file.name
                    
                    # Check if already exists (avoid duplicates)
                    if target_file.exists():
                        results["skipped_files"].append(post_file.name)
                        continue
                    
                    # Copy file
                    shutil.copy2(post_file, target_file)
                    results["synced_files"].append(post_file.name)
                    logger.info(f"Synced: {post_file.name}")
            
            # Sync HTML files to a static folder
            source_html = self.source_dir / "html"
            target_html = self.blog_dir / "static"
            target_html.mkdir(exist_ok=True)
            
            if source_html.exists():
                for html_file in source_html.glob("*.html"):
                    target_file = target_html / html_file.name
                    
                    if target_file.exists():
                        results["skipped_files"].append(f"static/{html_file.name}")
                        continue
                    
                    shutil.copy2(html_file, target_file)
                    results["synced_files"].append(f"static/{html_file.name}")
            
            # Regenerate index.html with all articles
            self._regenerate_index()
            
            # Update stats
            self._stats["total_synced"] += len(results["synced_files"])
            self._stats["last_sync"] = datetime.now(timezone.utc).isoformat()
            
            # Commit and push if there are changes
            if results["synced_files"] and push:
                push_result = await self._commit_and_push(
                    f"📝 Auto-sync: {len(results['synced_files'])} new articles"
                )
                results["pushed"] = push_result.get("success", False)
                results["push_result"] = push_result
            
            return {
                "status": "success",
                "results": results,
                "stats": self._stats
            }
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            results["errors"].append(str(e))
            return {"status": "error", "error": str(e), "results": results}
    
    async def _commit_and_push(self, message: str) -> Dict[str, Any]:
        """Commit changes and push to remote"""
        try:
            # Configure git
            subprocess.run(
                ["git", "config", "user.email", "kloud@pm.me"],
                cwd=self.blog_dir, check=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Kloud AI"],
                cwd=self.blog_dir, check=True
            )
            
            # Add all changes
            subprocess.run(["git", "add", "-A"], cwd=self.blog_dir, check=True)
            
            # Check if there are changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.blog_dir, capture_output=True, text=True
            )
            
            if not result.stdout.strip():
                return {"success": True, "message": "No changes to commit"}
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.blog_dir, check=True
            )
            
            # Push (use token auth if available)
            push_url = self.blog_repo_url
            if self.github_token and push_url and "github.com" in push_url:
                push_url = push_url.replace(
                    "https://github.com",
                    f"https://{self.github_token}@github.com"
                )
                subprocess.run(
                    ["git", "remote", "set-url", "origin", push_url],
                    cwd=self.blog_dir
                )
            
            result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=self.blog_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Try creating the branch first
                subprocess.run(
                    ["git", "branch", "-M", "main"],
                    cwd=self.blog_dir
                )
                result = subprocess.run(
                    ["git", "push", "-u", "origin", "main", "--force"],
                    cwd=self.blog_dir,
                    capture_output=True,
                    text=True
                )
            
            return {
                "success": result.returncode == 0,
                "message": "Pushed to remote" if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sync statistics"""
        return {
            **self._stats,
            "source_dir": str(self.source_dir),
            "blog_dir": str(self.blog_dir),
            "blog_repo": self.blog_repo_url,
            "initialized": self._initialized
        }


# Singleton instance
_blog_sync: Optional[BlogSync] = None


def get_blog_sync() -> BlogSync:
    """Get or create BlogSync instance"""
    global _blog_sync
    if _blog_sync is None:
        _blog_sync = BlogSync()
    return _blog_sync


# CLI interface
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    sync = BlogSync(
        source_dir=sys.argv[1] if len(sys.argv) > 1 else "/app/published",
        blog_repo_url=sys.argv[2] if len(sys.argv) > 2 else None
    )
    
    result = asyncio.run(sync.sync(push=True))
    print(json.dumps(result, indent=2))

