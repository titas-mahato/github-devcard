import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import config
from github_api import (
    get_login_url,
    exchange_code_for_token,
    get_authenticated_user,
    get_user_profile,
    get_user_repos,
    fetch_avatar_as_base64,
    calculate_stats,
)
from card_generator import generate_devcard_svg, get_sample_stats

# Initialize FastAPI App
app = FastAPI(
    title=config.APP_NAME,
    description="Generate dynamic SVG DevCards and live GitHub stats for profile READMEs via OAuth.",
    version="1.0.0",
)

# Enable encrypted session cookies
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, max_age=86400 * 7)

# Setup Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page showcasing live previews and OAuth login button."""
    user = request.session.get("user")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "base_url": config.BASE_URL,
        },
    )


@app.get("/login")
async def login(request: Request):
    """Initiate GitHub OAuth 2.0 authorization code flow."""
    if not config.GITHUB_CLIENT_ID or config.GITHUB_CLIENT_ID.startswith("your_"):
        return HTMLResponse(
            """
            <html>
                <body style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center;">
                    <div style="max-width: 600px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #334155;">
                        <h2 style="color: #38bdf8;">GitHub OAuth Credentials Required</h2>
                        <p style="color: #94a3b8; font-size: 14px; line-height: 1.6;">
                            To use live GitHub OAuth authentication, please configure your <code>GITHUB_CLIENT_ID</code> and <code>GITHUB_CLIENT_SECRET</code> in the <code>.env</code> file.
                        </p>
                        <p style="font-size: 13px; color: #cbd5e1;">See <b>GUIDE_PHASE1_OAUTH_SETUP.md</b> in this repository for step-by-step instructions.</p>
                        <div style="margin-top: 25px;">
                            <a href="/" style="background: #38bdf8; color: #0f172a; font-weight: bold; padding: 10px 20px; border-radius: 8px; text-decoration: none;">Return Home</a>
                            <a href="/api/preview-card" target="_blank" style="margin-left: 10px; background: #334155; color: #f8fafc; padding: 10px 20px; border-radius: 8px; text-decoration: none;">View Sample DevCard</a>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=400,
        )
    
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    login_url = get_login_url(state)
    return RedirectResponse(url=login_url)


@app.get("/callback")
async def oauth_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    """Handle OAuth redirect callback from GitHub."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from GitHub.")

    token = await exchange_code_for_token(code)
    if not token:
        raise HTTPException(status_code=401, detail="Failed to retrieve access token from GitHub.")

    user_data = await get_authenticated_user(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Failed to fetch user profile using OAuth token.")

    # Store user identity and token in session
    request.session["access_token"] = token
    request.session["user"] = {
        "login": user_data.get("login"),
        "name": user_data.get("name") or user_data.get("login"),
        "avatar_url": user_data.get("avatar_url"),
    }

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard showing live profile stats and custom SVG embed codes."""
    user = request.session.get("user")
    token = request.session.get("access_token")

    if not user or not token:
        return RedirectResponse(url="/login")

    username = user.get("login")
    profile = await get_user_profile(username, access_token=token)
    if not profile:
        profile = user

    repos = await get_user_repos(username, access_token=token)
    avatar_b64 = await fetch_avatar_as_base64(profile.get("avatar_url", ""))
    stats = calculate_stats(profile, repos, avatar_b64)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "base_url": config.BASE_URL,
        },
    )


@app.get("/api/card/{username}")
async def generate_user_card(
    username: str,
    request: Request,
    theme: Optional[str] = "midnight",
    download: Optional[int] = 0,
):
    """
    Public dynamic SVG DevCard endpoint.
    Can be embedded in any GitHub README: ![DevCard](https://your-domain.com/api/card/{username})
    """
    # Use session token if available to prevent rate limits
    token = request.session.get("access_token") if "request" in locals() else None

    profile = await get_user_profile(username, access_token=token)
    if not profile:
        # Generate friendly fallback card if user not found or rate limited
        sample = get_sample_stats()
        sample["username"] = username
        sample["name"] = f"User @{username}"
        sample["bio"] = "GitHub developer stats card."
        svg_content = generate_devcard_svg(sample, theme_name=theme or "midnight")
    else:
        repos = await get_user_repos(username, access_token=token)
        avatar_b64 = await fetch_avatar_as_base64(profile.get("avatar_url", ""))
        stats = calculate_stats(profile, repos, avatar_b64)
        svg_content = generate_devcard_svg(stats, theme_name=theme or "midnight")

    headers = {
        "Content-Type": "image/svg+xml; charset=utf-8",
        # 30 min browser cache, 1 hour GitHub Camo proxy revalidation
        "Cache-Control": "public, max-age=1800, s-maxage=1800, stale-while-revalidate=3600",
    }
    if download == 1:
        headers["Content-Disposition"] = f'attachment; filename="devcard-{username}.svg"'

    return Response(content=svg_content, media_type="image/svg+xml", headers=headers)


@app.get("/api/preview-card")
async def preview_card(theme: Optional[str] = "midnight"):
    """Instant sample SVG card endpoint for previewing themes without needing credentials."""
    sample = get_sample_stats()
    svg_content = generate_devcard_svg(sample, theme_name=theme or "midnight")
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Content-Type": "image/svg+xml; charset=utf-8",
            "Cache-Control": "no-cache",
        },
    )


@app.get("/logout")
async def logout(request: Request):
    """Log out and clear session."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
