# GitHub Profile DevCard & Stats Generator

A high-performance, lightweight web application built with Python FastAPI and OAuth 2.0 that generates dynamic vector SVG cards showing live GitHub statistics, repositories, and programming language distributions.

Designed specifically to be embedded directly into GitHub Profile README.md files.

---

## Features

- Standard OAuth 2.0 Web Flow: Authorize with GitHub using scoped permissions (read:user, repo).
- Real-time Statistics Aggregator: Calculates total stars earned across repositories, public repo counts, followers, and language percentages.
- Dynamic Vector SVG Generator: Zero external image processing dependencies. Embedded Base64 avatars comply with GitHub's camo proxy.
- Multiple Themes: Built-in support for midnight, cyberpunk, nord, dracula, slate, and light.
- Interactive Dashboard: 1-click Markdown and HTML embed snippet copying + direct SVG download.
- GitHub Developer Program Ready: Pre-configured structure and guides to register as an official GitHub Developer Program Member.

---

## Project Structure

```
github-devcard/
├── .env.example                     # Environment template
├── .env                             # Local environment secrets
├── requirements.txt                 # FastAPI & server dependencies
├── config.py                        # App configuration loader
├── main.py                          # FastAPI routing & OAuth flow
├── github_api.py                    # GitHub API client & stats engine
├── card_generator.py                # Pure Python dynamic SVG renderer
├── templates/
│   ├── base.html                    # Tailwind CSS layout
│   ├── index.html                   # Landing page with live preview
│   └── dashboard.html               # Authenticated metrics dashboard
└── README.md                        # Documentation
```

---

## Quickstart Guide

### 1. Activate Environment & Install Dependencies

```powershell
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy .env.example to .env and fill in your GitHub OAuth App credentials:

```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
BASE_URL=http://localhost:8000
SECRET_KEY=generate_a_random_secret_key
DEFAULT_THEME=midnight
```

*(Obtain your Client ID and Secret from GitHub Developer settings -> OAuth Apps).*

### 3. Launch the Server

```powershell
.\.venv\Scripts\uvicorn main:app --reload --port 8000
```

Open your browser at: http://localhost:8000

---

## Dynamic SVG Card API

You can generate dynamic DevCards for any public GitHub account directly via HTTP:

### Endpoint:
```http
GET /api/card/{username}?theme={theme_name}&download={0|1}
```

### GitHub Profile README Embed Example:
```markdown
[![My DevCard](https://your-domain.com/api/card/octocat?theme=midnight)](https://github.com/octocat)
```

---

## Deploying Publicly for GitHub READMEs

GitHub's markdown image proxy (camo) requires image URLs to be publicly reachable over HTTPS.

### Quick Options:
1. Cloudflare Tunnel or ngrok (for local testing):
   ```bash
   ngrok http 8000
   ```
   Update BASE_URL in .env to your https://xxxx.ngrok-free.app URL and update the Authorization Callback URL in GitHub OAuth settings.
2. Render / Railway / Fly.io / VPS (free/inexpensive production hosting):
   Deploy this repository directly as a Python web service with start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

---

## GitHub Developer Program

Register your OAuth app in your GitHub Developer settings to qualify as an official member of the GitHub Developer Program.
