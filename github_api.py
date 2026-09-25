import base64
from typing import Dict, Any, List, Optional
import httpx
from config import GITHUB_AUTH_URL, GITHUB_TOKEN_URL, GITHUB_API_BASE, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, BASE_URL

# Common GitHub language color map
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Rust": "#dea584",
    "Go": "#00ADD8",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Java": "#b07219",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Vue": "#41b883",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Shell": "#89e051",
    "Lua": "#000080",
    "R": "#198CE7",
    "Jupyter Notebook": "#DA5B0B",
    "Solidity": "#AA6746",
    "Scala": "#c22d40",
    "Elixir": "#6e4a7e",
    "Haskell": "#5e5086",
    "Zig": "#ec915c",
}
DEFAULT_LANG_COLOR = "#8b949e"


def get_login_url(state: Optional[str] = None) -> str:
    """Generate the GitHub OAuth authorization URL."""
    callback_url = f"{BASE_URL}/callback"
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": callback_url,
        "scope": "read:user repo",
    }
    if state:
        params["state"] = state
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GITHUB_AUTH_URL}?{query}"


async def exchange_code_for_token(code: str) -> Optional[str]:
    """Exchange temporary OAuth code for GitHub user access token."""
    callback_url = f"{BASE_URL}/callback"
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": callback_url,
    }
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(GITHUB_TOKEN_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
    return None


async def get_authenticated_user(access_token: str) -> Optional[Dict[str, Any]]:
    """Fetch current user profile using their OAuth access token."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-DevCard",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{GITHUB_API_BASE}/user", headers=headers)
        if response.status_code == 200:
            return response.json()
    return None


async def get_user_profile(username: str, access_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch public profile for a username, optionally with auth token for higher rate limits."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-DevCard",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{GITHUB_API_BASE}/users/{username}", headers=headers)
        if response.status_code == 200:
            return response.json()
    return None


async def get_user_repos(username: str, access_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch repositories for a user (up to 100)."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-DevCard",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    repos = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        # If authenticated user is looking at their own repos, use /user/repos to include authorized repos
        url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100&sort=pushed"
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            repos = response.json()
    return repos


async def fetch_avatar_as_base64(avatar_url: str) -> Optional[str]:
    """
    Fetch user avatar and convert to base64 data URI.
    Embedding image directly in SVG prevents GitHub Camo proxy from stripping external image links.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(avatar_url)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "image/png")
                encoded = base64.b64encode(resp.content).decode("ascii")
                return f"data:{content_type};base64,{encoded}"
    except Exception:
        pass
    return None


def calculate_stats(profile: Dict[str, Any], repos: List[Dict[str, Any]], avatar_base64: Optional[str] = None) -> Dict[str, Any]:
    """Calculate aggregated stars, forks, languages, and profile metrics."""
    total_stars = 0
    total_forks = 0
    lang_counts: Dict[str, int] = {}
    
    for repo in repos:
        if repo.get("fork"):
            # Exclude forks for accurate personal stats
            continue
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        lang = repo.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # Calculate language percentages
    total_lang_repos = sum(lang_counts.values()) or 1
    top_languages = []
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for lang, count in sorted_langs:
        pct = round((count / total_lang_repos) * 100, 1)
        color = LANGUAGE_COLORS.get(lang, DEFAULT_LANG_COLOR)
        top_languages.append({
            "name": lang,
            "count": count,
            "percentage": pct,
            "color": color,
        })

    return {
        "username": profile.get("login", "octocat"),
        "name": profile.get("name") or profile.get("login", "Developer"),
        "avatar_url": avatar_base64 or profile.get("avatar_url", ""),
        "bio": profile.get("bio") or "Passionate software engineer building open source projects.",
        "location": profile.get("location") or "",
        "company": profile.get("company") or "",
        "public_repos": profile.get("public_repos", len(repos)),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": top_languages,
        "created_year": (profile.get("created_at") or "2020")[:4],
    }
