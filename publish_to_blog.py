#!/usr/bin/env python3
"""
Publish documentation to kloud-blog GitHub repo.

Sistem publikimi për dokumenta në GitHub, nga ku publisheri merr
automatikisht dhe i poston në LinkedIn.

Usage:
    python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --title "L.A.G.T.E.R Protocols"
    python publish_to_blog.py --doc docs/NANOGRIDATA_SYSTEM_ARCHITECTURE.md
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re

class BlogPublisher:
    def __init__(self, blog_repo_url: str = "https://github.com/LedjanAhmati/kloud-blog.git"):
        self.blog_repo_url = blog_repo_url
        self.blog_dir = Path(".kloud-blog-tmp")
        self.posts_dir = self.blog_dir / "posts"
        self.metadata_file = self.blog_dir / "publications.json"
        
    def clone_or_update_repo(self) -> bool:
        """Clone or update the blog repository."""
        try:
            if self.blog_dir.exists():
                print(f"📦 Updating existing repo: {self.blog_dir}")
                result = subprocess.run(
                    ["git", "-C", str(self.blog_dir), "pull", "origin", "main"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"⚠️  Pull failed: {result.stderr}")
                    return False
            else:
                print(f"📦 Cloning blog repo: {self.blog_repo_url}")
                result = subprocess.run(
                    ["git", "clone", self.blog_repo_url, str(self.blog_dir)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"❌ Clone failed: {result.stderr}")
                    return False
            
            print("✅ Repository synced")
            return True
        except Exception as e:
            print(f"❌ Error syncing repo: {e}")
            return False
    
    def extract_metadata(self, doc_path: Path) -> Dict[str, Any]:
        """Extract or generate metadata from document."""
        content = doc_path.read_text(encoding="utf-8")
        
        # Parse YAML frontmatter if present
        frontmatter = {}
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker > 0:
                yaml_content = content[3:end_marker].strip()
                try:
                    import yaml
                    frontmatter = yaml.safe_load(yaml_content) or {}
                except ImportError:
                    # Fallback: parse simple key: value format
                    for line in yaml_content.split("\n"):
                        if ":" in line:
                            key, val = line.split(":", 1)
                            frontmatter[key.strip()] = val.strip()
        
        # Extract title from first heading
        title = frontmatter.get("title", "")
        if not title:
            match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if match:
                title = match.group(1)
        
        # Extract first paragraph as description
        description = frontmatter.get("description", "")
        if not description:
            # Skip frontmatter and title
            lines = content.split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#") and not line.startswith("---"):
                    description = line.strip()[:200]
                    break
        
        # Generate tags
        tags = frontmatter.get("tags", [])
        if not tags:
            # Auto-generate from filename and content
            filename = doc_path.stem.lower()
            tags = [t for t in filename.replace("_", "-").split("-") if t]
            
            # Add content-based tags
            keywords = {
                "lagter": ["protocols", "methodology", "industrial"],
                "nanogridata": ["iot", "gateway", "embedded", "security"],
                "architecture": ["design", "systems", "microservices"],
                "real": ["data", "pipeline", "production"],
            }
            for keyword, related_tags in keywords.items():
                if keyword in content.lower():
                    tags.extend(related_tags)
            
            tags = list(set(tags))[:5]  # Unique, max 5
        
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "published": frontmatter.get("published", datetime.utcnow().isoformat()),
            "author": frontmatter.get("author", "Kloud Team"),
            "image": frontmatter.get("image", ""),
            "source_file": str(doc_path),
            "content_hash": hash(content) & 0x7fffffff,
        }
    
    def prepare_post(self, doc_path: Path, metadata: Dict[str, Any]) -> tuple[str, str]:
        """Prepare post content with frontmatter."""
        content = doc_path.read_text(encoding="utf-8")
        
        # Remove existing frontmatter
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker > 0:
                content = content[end_marker + 3:].strip()
        
        # Create frontmatter
        frontmatter = f"""---
title: {metadata['title']}
description: {metadata['description']}
tags: {json.dumps(metadata['tags'])}
author: {metadata['author']}
published: {metadata['published']}
image: {metadata['image']}
source: https://github.com/LedjanAhmati/kloud-cloud/blob/main/{metadata['source_file']}
---

"""
        
        full_content = frontmatter + content
        
        # Generate slug from title
        slug = re.sub(r'[^\w\s-]', '', metadata['title'].lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        filename = f"{slug}.md"
        
        return filename, full_content
    
    def publish_document(self, doc_path: Path, title: Optional[str] = None) -> bool:
        """Publish a document to the blog."""
        doc_path = Path(doc_path)
        
        if not doc_path.exists():
            print(f"❌ Document not found: {doc_path}")
            return False
        
        print(f"\n📄 Publishing: {doc_path.name}")
        
        # Extract metadata
        metadata = self.extract_metadata(doc_path)
        if title:
            metadata["title"] = title
        
        print(f"   Title: {metadata['title']}")
        print(f"   Tags: {', '.join(metadata['tags'])}")
        
        # Prepare post
        filename, content = self.prepare_post(doc_path, metadata)
        post_path = self.posts_dir / filename
        
        # Write to blog repo
        post_path.parent.mkdir(parents=True, exist_ok=True)
        post_path.write_text(content, encoding="utf-8")
        
        print(f"   ✅ Written to: {post_path.relative_to(self.blog_dir)}")
        
        # Update publications.json
        self.update_publications_log(filename, metadata)
        
        return True
    
    def update_publications_log(self, filename: str, metadata: Dict[str, Any]) -> None:
        """Update publications.json tracking file."""
        if self.metadata_file.exists():
            publications = json.loads(self.metadata_file.read_text())
        else:
            publications = []
        
        # Check if already published
        existing = next((p for p in publications if p.get("filename") == filename), None)
        if existing:
            print(f"   ℹ️  Already tracked, updating...")
            existing.update({
                "title": metadata["title"],
                "updated": datetime.utcnow().isoformat(),
            })
        else:
            publications.append({
                "filename": filename,
                "title": metadata["title"],
                "tags": metadata["tags"],
                "published": metadata["published"],
                "updated": datetime.utcnow().isoformat(),
                "content_hash": metadata["content_hash"],
            })
        
        self.metadata_file.write_text(
            json.dumps(publications, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def commit_and_push(self, message: str = "docs: publish documentation") -> bool:
        """Commit and push changes to GitHub."""
        try:
            # Stage changes
            subprocess.run(
                ["git", "-C", str(self.blog_dir), "add", "-A"],
                capture_output=True,
                check=True
            )
            
            # Check if there are changes
            result = subprocess.run(
                ["git", "-C", str(self.blog_dir), "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                print("ℹ️  No changes to commit")
                return True
            
            # Commit
            subprocess.run(
                ["git", "-C", str(self.blog_dir), "commit", "-m", message],
                capture_output=True,
                check=True
            )
            
            # Push
            push_result = subprocess.run(
                ["git", "-C", str(self.blog_dir), "push", "origin", "main"],
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                print(f"✅ Pushed to GitHub: {message}")
                return True
            else:
                print(f"⚠️  Push failed: {push_result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Commit/push error: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up temporary directory."""
        if self.blog_dir.exists():
            import shutil
            shutil.rmtree(self.blog_dir)
            print("🧹 Cleaned up temporary files")


def main():
    parser = argparse.ArgumentParser(
        description="Publish documentation to kloud-blog GitHub repo"
    )
    parser.add_argument(
        "--doc",
        required=True,
        help="Path to documentation file to publish"
    )
    parser.add_argument(
        "--title",
        help="Custom title for the blog post (optional)"
    )
    parser.add_argument(
        "--repo",
        default="https://github.com/LedjanAhmati/kloud-blog.git",
        help="Blog repository URL"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push to GitHub (local only)"
    )
    parser.add_argument(
        "--keep-repo",
        action="store_true",
        help="Keep temporary repo directory"
    )
    parser.add_argument(
        "--status",
        choices=["APPROVED", "DRAFT"],
        default="DRAFT",
        help="Document approval status (must be APPROVED for production publish)"
    )
    
    args = parser.parse_args()
    
    # VALIDATION: Nuk publikojmë dokumenta pa aprovim
    if args.status != "APPROVED" and not args.no_push:
        print("\n[BLOCKED] PUBLIKIMI I BLLOKUAR")
        print("-" * 50)
        print("[INFO] Ky dokument nuk ka aprovim te plote.")
        print("\n[OK] Per te publikuar, duhet te:")
        print("   1. Te plotesojne 5 fazat e ristudimit")
        print("   2. Te merren miratimi nga te gjithe reviewers")
        print("   3. Te ruhet dokumenti i aprovimit ne /reviews")
        print("\n[LINK] Lexo: docs/DOCUMENT_REVIEW_PROCESS.md")
        print("-" * 50)
        sys.exit(1)
    
    publisher = BlogPublisher(args.repo)
    
    try:
        # Sync repo
        if not publisher.clone_or_update_repo():
            sys.exit(1)
        
        # Publish document
        if not publisher.publish_document(args.doc, args.title):
            sys.exit(1)
        
        # Push if requested
        if not args.no_push:
            doc_name = Path(args.doc).stem
            message = f"docs: publish {args.title or doc_name}"
            if not publisher.commit_and_push(message):
                print("⚠️  Warning: Commit/push failed, but document prepared locally")
        
        print("\n✅ Publication complete!")
        print(f"📍 Blog post available at: .kloud-blog-tmp/posts/")
        
    finally:
        if not args.keep_repo:
            publisher.cleanup()


if __name__ == "__main__":
    main()

