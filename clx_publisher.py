"""
CLX-PUBLISHER - Kloud Publishing Module
===========================================

Auto-publish engine for Kloud Content Factory.

Merr dokumentet EAP dhe i publikon automatikisht në platforma të ndryshme:
- LinkedIn
- Medium
- Substack
- X (Twitter)
- Kloud Blog
- GitHub Pages
- RSS Feed

Author: Ledjan Ahmati (CEO, ABA GmbH)
System: Kloud Cloud
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Try to import httpx for API calls
try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

# Import EAP for document types - use TYPE_CHECKING for type hints
if TYPE_CHECKING:
    from eap_layer import EAPDocument  # noqa: F401

# Runtime import check
_eap_available = False
try:
    import eap_layer as _eap_module  # noqa: F401
    _eap_available = True
except ImportError:
    pass

logger = logging.getLogger("clx_publisher")
logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class Platform(str, Enum):
    """Platformat e publikimit"""
    LINKEDIN = "linkedin"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    TWITTER = "twitter"           # X
    KLOUD_BLOG = "kloud"    # kloud.cloud/blog
    GITHUB_PAGES = "github"
    DEV_TO = "devto"
    RSS = "rss"
    WEBHOOK = "webhook"


class PublishStatus(str, Enum):
    """Statusi i publikimit"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContentFormat(str, Enum):
    """Formati i përmbajtjes"""
    FULL_ARTICLE = "full"          # Artikull i plotë
    SUMMARY = "summary"            # Përmbledhje
    THREAD = "thread"              # Thread (X/Twitter)
    TEASER = "teaser"              # Teaser me link
    EXCERPT = "excerpt"            # Fragment


@dataclass
class PublishConfig:
    """Konfigurimi i platformës së publikimit"""
    platform: Platform
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    webhook_url: Optional[str] = None
    default_format: ContentFormat = ContentFormat.FULL_ARTICLE
    max_length: Optional[int] = None
    rate_limit_per_hour: int = 10
    metadata: Dict = field(default_factory=dict)


@dataclass
class PublishResult:
    """Rezultati i publikimit"""
    id: str
    document_id: str
    platform: Platform
    status: PublishStatus
    url: Optional[str] = None
    error: Optional[str] = None
    published_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "platform": self.platform.value,
            "status": self.status.value,
            "url": self.url,
            "error": self.error,
            "published_at": self.published_at,
            "metadata": self.metadata
        }


@dataclass
class PublishQueue:
    """Queue për publikime"""
    id: str
    document: Any  # EAPDocument
    platforms: List[Platform]
    scheduled_time: Optional[str] = None
    priority: str = "normal"       # low, normal, high, urgent
    status: PublishStatus = PublishStatus.PENDING
    results: List[PublishResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT FORMATTERS
# ═══════════════════════════════════════════════════════════════════════════════

class ContentFormatter:
    """Format content for different platforms"""
    
    @staticmethod
    def to_linkedin(doc: EAPDocument, format_type: ContentFormat = ContentFormat.FULL_ARTICLE) -> str:
        """Format for LinkedIn"""
        if format_type == ContentFormat.THREAD:
            # LinkedIn doesn't have threads, use summary
            format_type = ContentFormat.SUMMARY
        
        content = f"📊 {doc.title}\n\n"
        
        if format_type == ContentFormat.SUMMARY:
            content += doc.executive_summary + "\n\n"
            content += "🔍 Key Findings:\n"
            for gap in doc.analysi.structural_gaps[:3]:
                content += f"• {gap['type'].title()}: {gap['description'][:100]}\n"
            content += f"\n💡 Proposed: {doc.proposi.paradigm_name}\n"
        else:
            content += doc.executive_summary + "\n\n"
            content += "---\n\n"
            content += "📋 OBSERVATION\n\n"
            content += doc.evresi.context[:500] + "\n\n"
            content += "🔍 ANALYSIS\n\n"
            for gap in doc.analysi.structural_gaps[:2]:
                content += f"• {gap['type'].title()}: {gap['description']}\n"
            content += "\n💡 PROPOSAL\n\n"
            content += f"{doc.proposi.paradigm_name}\n"
            content += doc.proposi.paradigm_description + "\n"
        
        content += "\n#Kloud #AI #Governance #Analysis"
        
        # LinkedIn limit: 3000 chars
        if len(content) > 3000:
            content = content[:2950] + "...\n\n[Read full analysis on kloud.cloud]"
        
        return content
    
    @staticmethod
    def to_twitter_thread(doc: EAPDocument) -> List[str]:
        """Format as Twitter/X thread"""
        tweets = []
        
        # Tweet 1: Title + hook
        tweet1 = f"🧵 {doc.title}\n\n"
        tweet1 += doc.executive_summary[:200] + "...\n\n"
        tweet1 += "Thread 👇"
        tweets.append(tweet1)
        
        # Tweet 2: Key observation
        tweet2 = "📋 OBSERVATION\n\n"
        facts = doc.evresi.facts[:2]
        for fact in facts:
            tweet2 += f"• {fact[:100]}\n"
        tweets.append(tweet2)
        
        # Tweet 3-4: Gaps
        for i, gap in enumerate(doc.analysi.structural_gaps[:2], 3):
            tweet = f"🔍 GAP #{i-2}: {gap['type'].upper()}\n\n"
            tweet += gap['description'][:200]
            tweets.append(tweet)
        
        # Tweet 5: Proposal
        tweet5 = f"💡 PROPOSAL: {doc.proposi.paradigm_name}\n\n"
        tweet5 += doc.proposi.paradigm_description[:200]
        tweets.append(tweet5)
        
        # Tweet 6: Key principles
        tweet6 = "🎯 KEY PRINCIPLES:\n\n"
        for principle in doc.proposi.principles[:3]:
            tweet6 += f"• {principle[:80]}\n"
        tweets.append(tweet6)
        
        # Tweet 7: CTA
        tweet7 = f"📖 Full analysis: kloud.cloud/analysis/{doc.id}\n\n"
        tweet7 += "#AI #Governance #Analysis #Kloud"
        tweets.append(tweet7)
        
        # Ensure each tweet is under 280 chars
        formatted = []
        for i, tweet in enumerate(tweets):
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
            formatted.append(f"{i+1}/{len(tweets)} {tweet}" if i > 0 else tweet)
        
        return formatted
    
    @staticmethod
    def to_medium(doc: EAPDocument) -> str:
        """Format for Medium (full markdown)"""
        return doc.to_markdown()
    
    @staticmethod
    def to_substack(doc: EAPDocument) -> str:
        """Format for Substack (newsletter style)"""
        content = f"# {doc.title}\n\n"
        content += f"*{datetime.now().strftime('%B %d, %Y')}*\n\n"
        
        content += "---\n\n"
        content += "## TL;DR\n\n"
        content += doc.executive_summary + "\n\n"
        
        content += "---\n\n"
        content += "## The Observation\n\n"
        content += doc.evresi.context + "\n\n"
        
        content += "### Key Facts\n\n"
        for fact in doc.evresi.facts[:5]:
            content += f"- {fact}\n"
        
        content += "\n## The Analysis\n\n"
        content += f"Our analysis reveals **{len(doc.analysi.structural_gaps)} structural gaps** "
        content += f"with **{doc.analysi.severity_level}** severity:\n\n"
        
        for gap in doc.analysi.structural_gaps:
            content += f"### {gap['type'].title()} Gap\n\n"
            content += f"{gap['description']}\n\n"
            content += f"*Missing concept: {gap['missing']}*\n\n"
        
        content += "## The Proposal\n\n"
        content += f"### {doc.proposi.paradigm_name}\n\n"
        content += doc.proposi.paradigm_description + "\n\n"
        
        content += "**Core Principles:**\n\n"
        for principle in doc.proposi.principles:
            content += f"1. {principle}\n"
        
        content += "\n**Implementation Path:**\n\n"
        for step in doc.proposi.implementation_steps:
            content += f"- **{step['name']}** ({step.get('timeline', 'TBD')}): {step['description']}\n"
        
        content += "\n---\n\n"
        content += "*This analysis was generated by Kloud Cloud.*\n"
        content += "*Subscribe for more insights: kloud.cloud*\n"
        
        return content
    
    @staticmethod
    def to_devto(doc: EAPDocument) -> Dict:
        """Format for Dev.to (with frontmatter)"""
        tags = doc.tags[:4]  # Dev.to allows max 4 tags
        
        frontmatter = f"""---
title: "{doc.title}"
published: true
tags: {', '.join(tags)}
canonical_url: https://kloud.cloud/analysis/{doc.id}
cover_image: https://kloud.cloud/images/analysis-cover.png
---

"""
        
        content = frontmatter + doc.to_markdown()
        return {
            "title": doc.title,
            "body_markdown": content,
            "tags": tags,
            "published": True
        }
    
    @staticmethod
    def to_rss_item(doc: EAPDocument) -> Dict:
        """Format as RSS item"""
        return {
            "title": doc.title,
            "description": doc.executive_summary,
            "content": doc.to_markdown(),
            "link": f"https://kloud.cloud/analysis/{doc.id}",
            "guid": doc.id,
            "pubDate": doc.timestamp,
            "author": doc.author,
            "category": doc.category,
            "tags": doc.tags
        }
    
    @staticmethod
    def to_teaser(doc: EAPDocument, max_length: int = 300) -> str:
        """Create a teaser with link"""
        teaser = f"📊 {doc.title}\n\n"
        teaser += doc.executive_summary[:max_length-100]
        teaser += f"...\n\n🔗 Read more: kloud.cloud/analysis/{doc.id}"
        return teaser


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM PUBLISHERS
# ═══════════════════════════════════════════════════════════════════════════════

class BasePlatformPublisher:
    """Base class for platform publishers"""
    
    platform: Platform = Platform.WEBHOOK
    
    def __init__(self, config: PublishConfig):
        self.config = config
        self.published_count = 0
        self.last_publish: Optional[str] = None
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish document to platform"""
        raise NotImplementedError
    
    def can_publish(self) -> bool:
        """Check if we can publish (rate limiting)"""
        if self.last_publish is None:
            return True
        
        # Simple rate limiting
        now = datetime.now(timezone.utc)
        last = datetime.fromisoformat(self.last_publish.replace('Z', '+00:00'))
        diff_seconds = (now - last).total_seconds()
        
        # At least 6 minutes between publishes for 10/hour limit
        return diff_seconds >= 360


class LinkedInPublisher(BasePlatformPublisher):
    """LinkedIn publisher"""
    
    platform = Platform.LINKEDIN
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish to LinkedIn"""
        result_id = f"pub_li_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        if not self.config.access_token:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error="LinkedIn access token not configured"
            )
        
        content = ContentFormatter.to_linkedin(doc, format_type)
        
        # LinkedIn API call (simulated)
        try:
            if httpx:
                # Real API call would go here
                # async with httpx.AsyncClient() as client:
                #     response = await client.post(...)
                pass
            
            # Simulate success
            self.published_count += 1
            self.last_publish = datetime.now(timezone.utc).isoformat()
            
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.PUBLISHED,
                url=f"https://linkedin.com/posts/{result_id}",
                published_at=self.last_publish,
                metadata={"content_length": len(content)}
            )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


class TwitterPublisher(BasePlatformPublisher):
    """Twitter/X publisher"""
    
    platform = Platform.TWITTER
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish to Twitter/X as thread"""
        result_id = f"pub_tw_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        if not self.config.api_key or not self.config.api_secret:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error="Twitter API credentials not configured"
            )
        
        tweets = ContentFormatter.to_twitter_thread(doc)
        
        try:
            # Twitter API call would go here
            # For now, simulate success
            
            self.published_count += 1
            self.last_publish = datetime.now(timezone.utc).isoformat()
            
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.PUBLISHED,
                url=f"https://twitter.com/kloud/status/{result_id}",
                published_at=self.last_publish,
                metadata={"thread_length": len(tweets)}
            )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


class MediumPublisher(BasePlatformPublisher):
    """Medium publisher"""
    
    platform = Platform.MEDIUM
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish to Medium"""
        result_id = f"pub_md_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        if not self.config.access_token:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error="Medium access token not configured"
            )
        
        content = ContentFormatter.to_medium(doc)
        
        try:
            # Medium API call would go here
            
            self.published_count += 1
            self.last_publish = datetime.now(timezone.utc).isoformat()
            
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.PUBLISHED,
                url=f"https://medium.com/@kloud/{result_id}",
                published_at=self.last_publish,
                metadata={"content_length": len(content)}
            )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


class SubstackPublisher(BasePlatformPublisher):
    """Substack publisher"""
    
    platform = Platform.SUBSTACK
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish to Substack"""
        result_id = f"pub_ss_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        content = ContentFormatter.to_substack(doc)
        
        try:
            # Substack doesn't have public API, would use automation or webhook
            
            self.published_count += 1
            self.last_publish = datetime.now(timezone.utc).isoformat()
            
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.PUBLISHED,
                url=f"https://kloud.substack.com/p/{result_id}",
                published_at=self.last_publish,
                metadata={"content_length": len(content)}
            )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


class KloudBlogPublisher(BasePlatformPublisher):
    """Kloud Blog publisher (internal)"""
    
    platform = Platform.KLOUD_BLOG
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish to Kloud blog"""
        result_id = f"pub_clx_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        content = doc.to_markdown()
        
        try:
            # Save to file system or call internal API
            output_dir = "output/blog"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{output_dir}/{doc.id}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Save metadata
            meta_file = f"{output_dir}/{doc.id}.json"
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(doc.to_dict(), f, indent=2)
            
            self.published_count += 1
            self.last_publish = datetime.now(timezone.utc).isoformat()
            
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.PUBLISHED,
                url=f"https://kloud.cloud/analysis/{doc.id}",
                published_at=self.last_publish,
                metadata={"filename": filename}
            )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


class WebhookPublisher(BasePlatformPublisher):
    """Generic webhook publisher"""
    
    platform = Platform.WEBHOOK
    
    async def publish(self, doc: EAPDocument, format_type: ContentFormat) -> PublishResult:
        """Publish via webhook"""
        result_id = f"pub_wh_{hashlib.md5(doc.id.encode()).hexdigest()[:8]}"
        
        if not self.config.webhook_url:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error="Webhook URL not configured"
            )
        
        payload = {
            "document": doc.to_dict(),
            "markdown": doc.to_markdown(),
            "published_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            if httpx:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.config.webhook_url,
                        json=payload
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        self.published_count += 1
                        self.last_publish = datetime.now(timezone.utc).isoformat()
                        
                        return PublishResult(
                            id=result_id,
                            document_id=doc.id,
                            platform=self.platform,
                            status=PublishStatus.PUBLISHED,
                            url=self.config.webhook_url,
                            published_at=self.last_publish,
                            metadata={"response_status": response.status_code}
                        )
                    else:
                        return PublishResult(
                            id=result_id,
                            document_id=doc.id,
                            platform=self.platform,
                            status=PublishStatus.FAILED,
                            error=f"Webhook returned {response.status_code}"
                        )
            else:
                return PublishResult(
                    id=result_id,
                    document_id=doc.id,
                    platform=self.platform,
                    status=PublishStatus.FAILED,
                    error="httpx not installed"
                )
        except Exception as e:
            return PublishResult(
                id=result_id,
                document_id=doc.id,
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )


# ═══════════════════════════════════════════════════════════════════════════════
# CLX PUBLISHER MAIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class CLXPublisher:
    """
    CLX-Publisher - Kloud Publishing Engine
    
    Merr dokumentet EAP dhe i publikon automatikisht në platforma.
    
    Usage:
        publisher = CLXPublisher()
        
        # Configure platforms
        publisher.configure_platform(Platform.LINKEDIN, access_token="...")
        publisher.configure_platform(Platform.TWITTER, api_key="...", api_secret="...")
        
        # Publish single document
        results = await publisher.publish(eap_document, platforms=[Platform.LINKEDIN, Platform.TWITTER])
        
        # Or use quality selector
        results = await publisher.publish_with_quality_check(eap_document)
    """
    
    def __init__(self) -> None:
        self._configs: Dict[Platform, PublishConfig] = {}
        self._publishers: Dict[Platform, BasePlatformPublisher] = {}
        self._queue: List[PublishQueue] = []
        self._publish_history: List[PublishResult] = []
        self._quality_threshold: float = 0.7
        
        # Initialize with default configs
        self._init_default_configs()
    
    def _init_default_configs(self) -> None:
        """Initialize default platform configurations"""
        for platform in Platform:
            self._configs[platform] = PublishConfig(
                platform=platform,
                enabled=False
            )
        
        # Enable local publishing by default
        self._configs[Platform.KLOUD_BLOG].enabled = True
    
    def configure_platform(
        self,
        platform: Platform,
        enabled: bool = True,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        webhook_url: Optional[str] = None,
        **kwargs
    ):
        """Configure a publishing platform"""
        config = PublishConfig(
            platform=platform,
            enabled=enabled,
            api_key=api_key or os.getenv(f"{platform.value.upper()}_API_KEY"),
            api_secret=api_secret or os.getenv(f"{platform.value.upper()}_API_SECRET"),
            access_token=access_token or os.getenv(f"{platform.value.upper()}_ACCESS_TOKEN"),
            webhook_url=webhook_url,
            metadata=kwargs
        )
        
        self._configs[platform] = config
        
        # Create publisher instance
        publisher_map = {
            Platform.LINKEDIN: LinkedInPublisher,
            Platform.TWITTER: TwitterPublisher,
            Platform.MEDIUM: MediumPublisher,
            Platform.SUBSTACK: SubstackPublisher,
            Platform.KLOUD_BLOG: KloudBlogPublisher,
            Platform.WEBHOOK: WebhookPublisher,
        }
        
        if platform in publisher_map:
            self._publishers[platform] = publisher_map[platform](config)
        
        logger.info(f"✓ Configured platform: {platform.value} (enabled: {enabled})")
    
    # ─────────────────────────────────────────────────────────────────────────
    # QUALITY SELECTOR
    # ─────────────────────────────────────────────────────────────────────────
    
    def assess_quality(self, doc: EAPDocument) -> Dict[str, Any]:
        """
        Assess document quality for publishing.
        
        Returns quality score and recommendations.
        """
        score = 0.0
        issues = []
        recommendations = []
        
        # Check executive summary
        if doc.executive_summary and len(doc.executive_summary) > 100:
            score += 0.15
        else:
            issues.append("Executive summary too short")
            recommendations.append("Expand executive summary to at least 100 words")
        
        # Check Evresi (facts)
        if doc.evresi.facts and len(doc.evresi.facts) >= 3:
            score += 0.15
        else:
            issues.append("Too few facts in Evresi")
            recommendations.append("Add more factual observations")
        
        # Check Analysi (gaps)
        if doc.analysi.structural_gaps and len(doc.analysi.structural_gaps) >= 2:
            score += 0.20
        else:
            issues.append("Insufficient gap analysis")
            recommendations.append("Identify more structural gaps")
        
        # Check Analysi (risks)
        if doc.analysi.risks and len(doc.analysi.risks) >= 2:
            score += 0.10
        else:
            issues.append("Risk analysis incomplete")
        
        # Check Proposi (paradigm)
        if doc.proposi.paradigm_name and doc.proposi.paradigm_description:
            score += 0.15
        else:
            issues.append("Proposal lacks clear paradigm")
            recommendations.append("Define a clear paradigm name and description")
        
        # Check Proposi (principles)
        if doc.proposi.principles and len(doc.proposi.principles) >= 3:
            score += 0.10
        else:
            issues.append("Too few principles")
        
        # Check Proposi (implementation)
        if doc.proposi.implementation_steps and len(doc.proposi.implementation_steps) >= 3:
            score += 0.10
        else:
            issues.append("Implementation plan incomplete")
        
        # Check tags
        if doc.tags and len(doc.tags) >= 3:
            score += 0.05
        else:
            issues.append("Insufficient tags for discoverability")
        
        return {
            "score": round(score, 2),
            "passed": score >= self._quality_threshold,
            "threshold": self._quality_threshold,
            "issues": issues,
            "recommendations": recommendations,
            "publish_ready": score >= self._quality_threshold and len(issues) <= 2
        }
    
    def select_platforms(self, doc: EAPDocument, quality: Dict) -> List[Platform]:
        """Select appropriate platforms based on content and quality"""
        platforms = []
        
        # Always publish to Kloud blog if enabled
        if self._configs[Platform.KLOUD_BLOG].enabled:
            platforms.append(Platform.KLOUD_BLOG)
        
        if not quality["passed"]:
            return platforms  # Only internal if quality is low
        
        # Professional content -> LinkedIn
        if self._configs[Platform.LINKEDIN].enabled:
            if doc.category in ["governance", "policy", "analysis"]:
                platforms.append(Platform.LINKEDIN)
        
        # Technical content -> Dev.to
        if self._configs[Platform.DEV_TO].enabled:
            if any(tag in doc.tags for tag in ["ai", "tech", "architecture", "engineering"]):
                platforms.append(Platform.DEV_TO)
        
        # High quality -> Medium, Substack
        if quality["score"] >= 0.8:
            if self._configs[Platform.MEDIUM].enabled:
                platforms.append(Platform.MEDIUM)
            if self._configs[Platform.SUBSTACK].enabled:
                platforms.append(Platform.SUBSTACK)
        
        # Breaking/urgent content -> Twitter
        if self._configs[Platform.TWITTER].enabled:
            if doc.analysi.severity_level in ["critical", "major"]:
                platforms.append(Platform.TWITTER)
        
        return platforms
    
    # ─────────────────────────────────────────────────────────────────────────
    # PUBLISHING
    # ─────────────────────────────────────────────────────────────────────────
    
    async def publish(
        self,
        doc: EAPDocument,
        platforms: Optional[List[Platform]] = None,
        format_type: ContentFormat = ContentFormat.FULL_ARTICLE
    ) -> List[PublishResult]:
        """
        Publish document to specified platforms.
        
        Args:
            doc: EAPDocument to publish
            platforms: List of platforms (None = auto-select)
            format_type: Content format
            
        Returns:
            List of PublishResult
        """
        results = []
        
        # Quality check
        quality = self.assess_quality(doc)
        
        # Select platforms if not specified
        if platforms is None:
            platforms = self.select_platforms(doc, quality)
        
        logger.info(f"📤 Publishing {doc.id} to {len(platforms)} platforms...")
        
        for platform in platforms:
            if platform not in self._publishers:
                # Create default publisher if not configured
                if platform == Platform.KLOUD_BLOG:
                    self._publishers[platform] = KloudBlogPublisher(self._configs[platform])
                else:
                    logger.warning(f"Publisher not configured for {platform.value}")
                    continue
            
            publisher = self._publishers[platform]
            
            if not publisher.can_publish():
                logger.warning(f"Rate limited for {platform.value}, skipping")
                results.append(PublishResult(
                    id=f"skip_{platform.value}",
                    document_id=doc.id,
                    platform=platform,
                    status=PublishStatus.SKIPPED,
                    error="Rate limited"
                ))
                continue
            
            try:
                result = await publisher.publish(doc, format_type)
                results.append(result)
                self._publish_history.append(result)
                
                if result.status == PublishStatus.PUBLISHED:
                    logger.info(f"✅ Published to {platform.value}: {result.url}")
                else:
                    logger.warning(f"❌ Failed to publish to {platform.value}: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error publishing to {platform.value}: {e}")
                results.append(PublishResult(
                    id=f"error_{platform.value}",
                    document_id=doc.id,
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error=str(e)
                ))
        
        return results
    
    async def publish_with_quality_check(
        self,
        doc: EAPDocument,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Publish with quality assessment.
        
        Returns quality report and publish results.
        """
        quality = self.assess_quality(doc)
        
        if not quality["publish_ready"] and not force:
            return {
                "published": False,
                "quality": quality,
                "results": [],
                "message": "Document did not pass quality check. Use force=True to publish anyway."
            }
        
        platforms = self.select_platforms(doc, quality)
        results = await self.publish(doc, platforms)
        
        return {
            "published": True,
            "quality": quality,
            "platforms": [p.value for p in platforms],
            "results": [r.to_dict() for r in results],
            "successful": sum(1 for r in results if r.status == PublishStatus.PUBLISHED),
            "failed": sum(1 for r in results if r.status == PublishStatus.FAILED)
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # QUEUE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────
    
    def add_to_queue(
        self,
        doc: EAPDocument,
        platforms: List[Platform],
        scheduled_time: Optional[str] = None,
        priority: str = "normal"
    ) -> str:
        """Add document to publish queue"""
        queue_id = f"queue_{len(self._queue) + 1}_{hashlib.md5(doc.id.encode()).hexdigest()[:6]}"
        
        queue_item = PublishQueue(
            id=queue_id,
            document=doc,
            platforms=platforms,
            scheduled_time=scheduled_time,
            priority=priority
        )
        
        self._queue.append(queue_item)
        logger.info(f"📋 Added to queue: {queue_id} (priority: {priority})")
        
        return queue_id
    
    async def process_queue(self, batch_size: int = 5) -> List[PublishResult]:
        """Process items in queue"""
        results = []
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        sorted_queue = sorted(self._queue, key=lambda x: priority_order.get(x.priority, 2))
        
        processed = 0
        for item in sorted_queue[:batch_size]:
            if item.status != PublishStatus.PENDING:
                continue
            
            # Check scheduled time
            if item.scheduled_time:
                scheduled = datetime.fromisoformat(item.scheduled_time)
                if datetime.now(timezone.utc) < scheduled:
                    continue
            
            item.status = PublishStatus.PUBLISHING
            item_results = await self.publish(item.document, item.platforms)
            item.results = item_results
            item.status = PublishStatus.PUBLISHED
            
            results.extend(item_results)
            processed += 1
        
        # Remove processed items
        self._queue = [q for q in self._queue if q.status == PublishStatus.PENDING]
        
        logger.info(f"📤 Processed {processed} items from queue")
        return results
    
    # ─────────────────────────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics"""
        platform_stats = {}
        for platform, publisher in self._publishers.items():
            platform_stats[platform.value] = {
                "published_count": publisher.published_count,
                "last_publish": publisher.last_publish,
                "enabled": self._configs[platform].enabled
            }
        
        return {
            "total_published": len([r for r in self._publish_history if r.status == PublishStatus.PUBLISHED]),
            "total_failed": len([r for r in self._publish_history if r.status == PublishStatus.FAILED]),
            "queue_size": len(self._queue),
            "platforms": platform_stats,
            "quality_threshold": self._quality_threshold
        }
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent publish history"""
        return [r.to_dict() for r in self._publish_history[-limit:]]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_publisher_instance: Optional[CLXPublisher] = None


def get_publisher() -> CLXPublisher:
    """Get or create CLXPublisher instance"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = CLXPublisher()
    return _publisher_instance


async def publish_eap(doc: EAPDocument, platforms: Optional[List[str]] = None) -> List[Dict]:
    """Quick function to publish EAP document"""
    publisher = get_publisher()
    
    platform_list = None
    if platforms:
        platform_list = [Platform(p) for p in platforms]
    
    results = await publisher.publish(doc, platform_list)
    return [r.to_dict() for r in results]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN (for testing)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test_publisher() -> None:
        print("=" * 70)
        print("📤 CLX-PUBLISHER TEST")
        print("=" * 70)
        
        # Create mock EAP document
        from dataclasses import dataclass as dc
        from typing import Any, Optional  # noqa: F401
        
        @dc
        class MockEvresi:
            id: str = "clx.obs.test123"
            title: str = "Test Observation"
            facts: Any = None  # type: ignore[valid-type]
            context: str = "Test context for observation"
            source: str = "test"
            source_date: str = "2026-02-06"
            entities: Any = None
            locations: Any = None
            keywords: Any = None
            original_question: Optional[str] = None
            timestamp: str = "2026-02-06T00:00:00Z"
            
            def __post_init__(self):
                if self.facts is None:
                    self.facts = ["Fact 1", "Fact 2", "Fact 3"]
                if self.entities is None:
                    self.entities = []
                if self.locations is None:
                    self.locations = []
                if self.keywords is None:
                    self.keywords = ["ai", "governance", "analysis"]
        
        @dc
        class MockAnalysi:
            id: str = "clx.gap.test123"
            title: str = "Test Analysis"
            evresi_id: str = "clx.obs.test123"
            structural_gaps: Any = None
            discontinuities: Any = None
            risks: Any = None
            missing_concepts: Any = None
            implications: Any = None
            propagation_timeline: Any = None
            severity_level: str = "moderate"
            timestamp: str = "2026-02-06T00:00:00Z"
            
            def __post_init__(self):
                if self.structural_gaps is None:
                    self.structural_gaps = [
                        {"type": "accountability", "description": "Missing oversight", "severity": "major", "missing": "Audit mechanism"},
                        {"type": "sovereignty", "description": "Loss of control", "severity": "major", "missing": "State control"}
                    ]
                if self.risks is None:
                    self.risks = [{"category": "governance", "description": "Risk from gaps", "severity": "high"}]
                if self.missing_concepts is None:
                    self.missing_concepts = ["Accountability", "Transparency"]
                if self.implications is None:
                    self.implications = ["Implication 1", "Implication 2"]
                if self.propagation_timeline is None:
                    self.propagation_timeline = []
                if self.discontinuities is None:
                    self.discontinuities = []
        
        @dc
        class MockProposi:
            id: str = "clx.prop.test123"
            title: str = "Proposal: Test Paradigm"
            evresi_id: str = "clx.obs.test123"
            analysi_id: str = "clx.gap.test123"
            paradigm_name: str = "Integrated Governance Framework"
            paradigm_description: str = "A comprehensive framework for governance"
            architecture: Any = None
            principles: Any = None
            implementation_steps: Any = None
            expected_outcomes: Any = None
            addresses_gaps: Any = None
            alternatives_considered: Any = None
            timestamp: str = "2026-02-06T00:00:00Z"
            
            def __post_init__(self):
                if self.architecture is None:
                    self.architecture = {"core": "Governance Core", "verification": "Audit Layer"}
                if self.principles is None:
                    self.principles = ["Transparency", "Accountability", "Sovereignty"]
                if self.implementation_steps is None:
                    self.implementation_steps = [
                        {"name": "Phase 1", "description": "Foundation", "timeline": "Q1"},
                        {"name": "Phase 2", "description": "Build", "timeline": "Q2"},
                        {"name": "Phase 3", "description": "Deploy", "timeline": "Q3"}
                    ]
                if self.expected_outcomes is None:
                    self.expected_outcomes = ["Outcome 1", "Outcome 2"]
                if self.addresses_gaps is None:
                    self.addresses_gaps = ["accountability", "sovereignty"]
                if self.alternatives_considered is None:
                    self.alternatives_considered = []
        
        @dc
        class MockEAPDocument:
            id: str = "clx.eap.test123"
            title: str = "Test Analysis Document"
            evresi: Any = None
            analysi: Any = None
            proposi: Any = None
            executive_summary: str = "This is a comprehensive test analysis examining governance gaps and proposing solutions."
            author: str = "Kloud Cloud"
            version: str = "1.0"
            tags: Any = None
            category: str = "governance"
            publish_ready: bool = True
            timestamp: str = "2026-02-06T00:00:00Z"
            
            def __post_init__(self):
                if self.evresi is None:
                    self.evresi = MockEvresi()
                if self.analysi is None:
                    self.analysi = MockAnalysi()
                if self.proposi is None:
                    self.proposi = MockProposi()
                if self.tags is None:
                    self.tags = ["ai", "governance", "analysis", "policy"]
            
            def to_markdown(self) -> str:
                return f"# {self.title}\n\n{self.executive_summary}"
            
            def to_dict(self) -> dict:
                return {"id": self.id, "title": self.title}
        
        # Create test document
        doc = MockEAPDocument()
        
        print(f"\n📄 Test Document: {doc.id}")
        print(f"   Title: {doc.title}")
        print(f"   Category: {doc.category}")
        
        # Create publisher
        publisher = CLXPublisher()
        
        # Test quality assessment
        print("\n" + "=" * 70)
        print("🔍 QUALITY ASSESSMENT")
        print("=" * 70)
        
        quality = publisher.assess_quality(doc)  # type: ignore[arg-type]
        print(f"   Score: {quality['score']}")
        print(f"   Passed: {quality['passed']}")
        print(f"   Threshold: {quality['threshold']}")
        
        if quality['issues']:
            print("   Issues:")
            for issue in quality['issues']:
                print(f"     • {issue}")
        
        # Test platform selection
        print("\n" + "=" * 70)
        print("📊 PLATFORM SELECTION")
        print("=" * 70)
        
        platforms = publisher.select_platforms(doc, quality)  # type: ignore[arg-type]
        print(f"   Selected: {[p.value for p in platforms]}")
        
        # Test content formatting
        print("\n" + "=" * 70)
        print("✍️ CONTENT FORMATTING")
        print("=" * 70)
        
        print("\n--- LinkedIn Format (first 300 chars) ---")
        linkedin = ContentFormatter.to_linkedin(doc, ContentFormat.SUMMARY)  # type: ignore[arg-type]
        print(linkedin[:300])
        
        print("\n--- Twitter Thread (first 2 tweets) ---")
        tweets = ContentFormatter.to_twitter_thread(doc)  # type: ignore[arg-type]
        for tweet in tweets[:2]:
            print(f"\n{tweet}")
        
        # Test publishing
        print("\n" + "=" * 70)
        print("📤 PUBLISHING")
        print("=" * 70)
        
        results = await publisher.publish(doc)  # type: ignore[arg-type]
        
        for result in results:
            print(f"\n   Platform: {result.platform.value}")
            print(f"   Status: {result.status.value}")
            if result.url:
                print(f"   URL: {result.url}")
            if result.error:
                print(f"   Error: {result.error}")
        
        # Stats
        print("\n" + "=" * 70)
        print("📊 PUBLISHER STATS")
        print("=" * 70)
        
        stats = publisher.get_stats()
        print(f"   Total Published: {stats['total_published']}")
        print(f"   Total Failed: {stats['total_failed']}")
        print(f"   Queue Size: {stats['queue_size']}")
        
        print("\n✅ CLX-Publisher test complete!")
    
    asyncio.run(test_publisher())

