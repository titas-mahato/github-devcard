import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the current directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
SECRET_KEY = os.getenv("SECRET_KEY", "devcard-insecure-secret-key-please-change")
DEFAULT_THEME = os.getenv("DEFAULT_THEME", "midnight")
APP_NAME = os.getenv("APP_NAME", "GitHub Profile DevCard & Stats Generator")


# GitHub OAuth endpoints
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE = "https://api.github.com"

# Requested OAuth scopes
# 'read:user' grants access to profile information and email
# 'public_repo' or 'repo' (optional) grants access to repository data
GITHUB_SCOPES = "read:user"
