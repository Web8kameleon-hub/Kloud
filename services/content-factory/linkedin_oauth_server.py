"""
LinkedIn OAuth Server - Kloud Content Factory
=================================================

Endpoint për LinkedIn OAuth dhe auto-publishing.

Autor: Ledjan Ahmati (CEO, ABA GmbH)
"""

import logging
import os
import secrets
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linkedin_oauth")

app = FastAPI(
    title="Kloud LinkedIn Integration",
    description="OAuth dhe Auto-Publishing për LinkedIn",
    version="1.0.0"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.environ.get("LINKEDIN_REDIRECT_URI", "https://kloud.com/api/linkedin/callback")
LINKEDIN_ORGANIZATION_URN = os.environ.get("LINKEDIN_ORGANIZATION_URN", "urn:li:organization:111866162")

# OAuth scopes for organization posting
LINKEDIN_SCOPES = [
    "w_organization_social",    # Post on behalf of organization
    "r_organization_social",    # Read organization posts
    "rw_organization_admin",    # Admin access to organization
]

# State storage (in production, use Redis)
oauth_states: dict = {}


# ═══════════════════════════════════════════════════════════════════════════════
# OAUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "linkedin-oauth"}


@app.get("/api/linkedin/auth")
async def start_linkedin_auth():
    """
    Start LinkedIn OAuth flow.
    Redirects user to LinkedIn authorization page.
    """
    if not LINKEDIN_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="LINKEDIN_CLIENT_ID not configured. Add it to environment."
        )
    
    # Generate secure state
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    # Build authorization URL
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code"
        f"&client_id={LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={LINKEDIN_REDIRECT_URI}"
        f"&state={state}"
        f"&scope={' '.join(LINKEDIN_SCOPES)}"
    )
    
    logger.info("Starting LinkedIn OAuth flow, redirecting to LinkedIn...")
    return RedirectResponse(url=auth_url)


@app.get("/api/linkedin/callback")
async def linkedin_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_description: str = Query(None)
):
    """
    LinkedIn OAuth callback handler.
    Exchanges authorization code for access token.
    """
    if error:
        logger.error(f"LinkedIn OAuth error: {error} - {error_description}")
        return JSONResponse(
            status_code=400,
            content={"error": error, "description": error_description}
        )
    
    # Validate state
    if not state or state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    del oauth_states[state]  # Use state only once
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINKEDIN_REDIRECT_URI,
                "client_id": LINKEDIN_CLIENT_ID,
                "client_secret": LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    if token_response.status_code != 200:
        logger.error(f"Token exchange failed: {token_response.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Token exchange failed: {token_response.text}"
        )
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 5184000)  # ~60 days
    
    logger.info(f"LinkedIn OAuth successful! Token expires in {expires_in} seconds")
    
    # In production: save to database/secrets
    # For now: return to user to manually set
    return JSONResponse({
        "success": True,
        "message": "LinkedIn connected successfully!",
        "access_token": access_token,
        "expires_in": expires_in,
        "instructions": (
            "Add this to your environment:\n"
            f"LINKEDIN_ACCESS_TOKEN={access_token}"
        )
    })


# ═══════════════════════════════════════════════════════════════════════════════
# POSTING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/linkedin/post")
async def create_linkedin_post(
    commentary: str,
    article_url: Optional[str] = None,
    article_title: Optional[str] = None,
    article_description: Optional[str] = None
):
    """
    Create a LinkedIn post for the organization.
    
    Args:
        commentary: Post text (max 3000 chars)
        article_url: Optional article URL to share
        article_title: Article title (if sharing article)
        article_description: Article description (if sharing article)
    """
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not connected to LinkedIn. Visit /api/linkedin/auth first."
        )
    
    # Build post payload
    post_data = {
        "author": LINKEDIN_ORGANIZATION_URN,
        "commentary": commentary[:3000],  # LinkedIn limit
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    
    # Add article content if provided
    if article_url:
        post_data["content"] = {
            "article": {
                "source": article_url,
                "title": article_title or "Read more",
                "description": article_description or ""
            }
        }
    
    # Post to LinkedIn
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linkedin.com/rest/posts",
            json=post_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
                "LinkedIn-Version": "202601"  # Current version
            }
        )
    
    if response.status_code == 201:
        post_id = response.headers.get("x-restli-id", "unknown")
        logger.info(f"LinkedIn post created: {post_id}")
        return {
            "success": True,
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/update/{post_id}"
        }
    else:
        logger.error(f"LinkedIn post failed: {response.text}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"LinkedIn API error: {response.text}"
        )


@app.get("/api/linkedin/posts")
async def get_organization_posts(count: int = 10):
    """
    Get recent posts from the organization.
    """
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not connected to LinkedIn")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.linkedin.com/rest/posts",
            params={
                "author": LINKEDIN_ORGANIZATION_URN.replace(":", "%3A"),
                "q": "author",
                "count": count,
                "sortBy": "LAST_MODIFIED"
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "LinkedIn-Version": "202601"
            }
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch posts: {response.text}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     🔗 KLOUD LINKEDIN INTEGRATION SERVER                       ║
╠═══════════════════════════════════════════════════════════════════╣
║  1. Set environment variables:                                    ║
║     - LINKEDIN_CLIENT_ID                                          ║
║     - LINKEDIN_CLIENT_SECRET                                      ║
║                                                                   ║
║  2. Visit /api/linkedin/auth to connect                           ║
║  3. Use /api/linkedin/post to publish articles                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8040)

