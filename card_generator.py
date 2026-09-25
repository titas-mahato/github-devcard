from typing import Dict, Any, List
import html

# Theme color configurations
THEMES = {
    "midnight": {
        "bg_gradient_start": "#0f172a",
        "bg_gradient_end": "#020617",
        "border": "#1e293b",
        "title": "#f8fafc",
        "subtitle": "#94a3b8",
        "text": "#cbd5e1",
        "accent": "#38bdf8",
        "card_bg": "#1e293b80",
        "bar_bg": "#334155",
        "badge_border": "#334155",
    },
    "cyberpunk": {
        "bg_gradient_start": "#0f051d",
        "bg_gradient_end": "#1f0322",
        "border": "#f72585",
        "title": "#4cc9f0",
        "subtitle": "#f72585",
        "text": "#e0aaff",
        "accent": "#f72585",
        "card_bg": "#2b093880",
        "bar_bg": "#3c096c",
        "badge_border": "#7209b7",
    },
    "nord": {
        "bg_gradient_start": "#2e3440",
        "bg_gradient_end": "#242933",
        "border": "#434c5e",
        "title": "#eceff4",
        "subtitle": "#88c0d0",
        "text": "#d8dee9",
        "accent": "#88c0d0",
        "card_bg": "#3b425280",
        "bar_bg": "#4c566a",
        "badge_border": "#4c566a",
    },
    "dracula": {
        "bg_gradient_start": "#282a36",
        "bg_gradient_end": "#1e1f29",
        "border": "#6272a4",
        "title": "#50fa7b",
        "subtitle": "#bd93f9",
        "text": "#f8f8f2",
        "accent": "#ff79c6",
        "card_bg": "#44475a80",
        "bar_bg": "#6272a4",
        "badge_border": "#6272a4",
    },
    "slate": {
        "bg_gradient_start": "#1e293b",
        "bg_gradient_end": "#0f172a",
        "border": "#334155",
        "title": "#f1f5f9",
        "subtitle": "#94a3b8",
        "text": "#cbd5e1",
        "accent": "#60a5fa",
        "card_bg": "#33415580",
        "bar_bg": "#475569",
        "badge_border": "#475569",
    },
    "light": {
        "bg_gradient_start": "#ffffff",
        "bg_gradient_end": "#f8fafc",
        "border": "#e2e8f0",
        "title": "#0f172a",
        "subtitle": "#64748b",
        "text": "#334155",
        "accent": "#2563eb",
        "card_bg": "#f1f5f980",
        "bar_bg": "#e2e8f0",
        "badge_border": "#cbd5e1",
    },
}


def escape(text: Any) -> str:
    """Safely escape text for XML/SVG rendering."""
    return html.escape(str(text or ""))


def generate_devcard_svg(stats: Dict[str, Any], theme_name: str = "midnight") -> str:
    """Generate high-resolution, responsive dynamic SVG DevCard for GitHub profile READMEs."""
    theme = THEMES.get(theme_name.lower(), THEMES["midnight"])

    name = escape(stats.get("name", "GitHub Developer")[:26])
    username = escape(stats.get("username", "developer"))
    bio = escape(stats.get("bio", "")[:50] + ("..." if len(stats.get("bio", "")) > 50 else ""))
    
    total_stars = escape(stats.get("total_stars", 0))
    public_repos = escape(stats.get("public_repos", 0))
    followers = escape(stats.get("followers", 0))
    total_forks = escape(stats.get("total_forks", 0))
    
    avatar_url = stats.get("avatar_url", "")
    languages: List[Dict[str, Any]] = stats.get("languages", [])

    # Calculate language progress bar segments
    bar_width = 460
    bar_svg_parts = []
    current_x = 0
    total_pct = sum(l.get("percentage", 0) for l in languages) or 100

    for lang in languages:
        pct = lang.get("percentage", 0)
        seg_width = (pct / total_pct) * bar_width
        color = lang.get("color", "#888888")
        if seg_width > 0:
            bar_svg_parts.append(
                f'<rect x="{current_x:.1f}" y="0" width="{seg_width:.1f}" height="8" fill="{color}" />'
            )
            current_x += seg_width

    progress_bar_markup = "".join(bar_svg_parts) if bar_svg_parts else f'<rect x="0" y="0" width="{bar_width}" height="8" fill="{theme["bar_bg"]}" />'

    # Build language legend items
    legend_items = []
    legend_x = 40
    legend_y = 230
    for i, lang in enumerate(languages[:4]):
        l_name = escape(lang.get("name", ""))
        l_pct = lang.get("percentage", 0)
        l_color = lang.get("color", "#888888")
        item_x = legend_x + (i * 115)
        legend_items.append(
            f'''
            <g transform="translate({item_x}, {legend_y})">
                <circle cx="5" cy="5" r="4.5" fill="{l_color}"/>
                <text x="14" y="8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11" font-weight="500" fill="{theme['text']}">{l_name} <tspan fill="{theme['subtitle']}" font-size="10">{l_pct}%</tspan></text>
            </g>
            '''
        )
    legend_markup = "".join(legend_items)

    # Avatar image tag or fallback monogram
    if avatar_url:
        avatar_markup = f'''
        <image href="{avatar_url}" x="40" y="28" width="58" height="58" clip-path="url(#avatar-clip)" preserveAspectRatio="xMidYMid slice"/>
        '''
    else:
        initial = (stats.get("name") or stats.get("username") or "G")[:1].upper()
        avatar_markup = f'''
        <circle cx="69" cy="57" r="29" fill="{theme['accent']}" opacity="0.2"/>
        <text x="69" y="66" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="24" font-weight="700" fill="{theme['accent']}">{initial}</text>
        '''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="540" height="260" viewBox="0 0 540 260" fill="none">
    <defs>
        <linearGradient id="card-bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{theme['bg_gradient_start']}"/>
            <stop offset="100%" stop-color="{theme['bg_gradient_end']}"/>
        </linearGradient>
        <clipPath id="avatar-clip">
            <circle cx="69" cy="57" r="29"/>
        </clipPath>
        <clipPath id="bar-clip">
            <rect x="0" y="0" width="460" height="8" rx="4" ry="4"/>
        </clipPath>
        <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="110%">
            <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.35"/>
        </filter>
    </defs>

    <style>
        .title {{ font: 600 17px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['title']}; }}
        .subtitle {{ font: 400 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['subtitle']}; }}
        .bio {{ font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['text']}; }}
        .stat-value {{ font: 700 15px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['title']}; }}
        .stat-label {{ font: 500 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['subtitle']}; text-transform: uppercase; letter-spacing: 0.5px; }}
        .badge-bg {{ fill: {theme['card_bg']}; stroke: {theme['badge_border']}; stroke-width: 1px; rx: 8px; }}
        .section-label {{ font: 600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {theme['subtitle']}; letter-spacing: 0.5px; text-transform: uppercase; }}
        .dev-badge {{ fill: {theme['accent']}; }}
    </style>

    <!-- Card Background -->
    <rect x="4" y="4" width="532" height="252" rx="16" ry="16" fill="url(#card-bg)" stroke="{theme['border']}" stroke-width="1.5" filter="url(#card-shadow)"/>

    <!-- Avatar Outline & Image -->
    <circle cx="69" cy="57" r="31" fill="none" stroke="{theme['accent']}" stroke-width="2" opacity="0.8"/>
    {avatar_markup}

    <!-- User Header Info -->
    <g transform="translate(112, 38)">
        <text class="title" x="0" y="0">{name}</text>
        <!-- GitHub Developer Verified Star Icon -->
        <path class="dev-badge" transform="translate(185, -12) scale(0.7)" d="M12 2l2.4 4.8 5.3.8-3.8 3.7.9 5.3L12 16.1l-4.8 2.5.9-5.3-3.8-3.7 5.3-.8L12 2z"/>
        <text class="subtitle" x="0" y="18">@{username}</text>
        <text class="bio" x="0" y="34">{bio}</text>
    </g>

    <!-- Metrics Stat Badges (Stars, Repos, Followers, Forks) -->
    <!-- Metric 1: Total Stars -->
    <g transform="translate(40, 102)">
        <rect class="badge-bg" width="107" height="46"/>
        <path fill="#eab308" transform="translate(10, 14) scale(0.75)" d="M12 2l2.4 4.8 5.3.8-3.8 3.7.9 5.3L12 16.1l-4.8 2.5.9-5.3-3.8-3.7 5.3-.8L12 2z"/>
        <text class="stat-value" x="32" y="24">{total_stars}</text>
        <text class="stat-label" x="32" y="38">Stars</text>
    </g>

    <!-- Metric 2: Public Repos -->
    <g transform="translate(157, 102)">
        <rect class="badge-bg" width="107" height="46"/>
        <path fill="{theme['accent']}" transform="translate(10, 14) scale(0.75)" d="M4 2v20h16V2H4zm2 2h12v16H6V4zm2 2v4h8V6H8z"/>
        <text class="stat-value" x="32" y="24">{public_repos}</text>
        <text class="stat-label" x="32" y="38">Repos</text>
    </g>

    <!-- Metric 3: Followers -->
    <g transform="translate(275, 102)">
        <rect class="badge-bg" width="107" height="46"/>
        <path fill="#ec4899" transform="translate(10, 14) scale(0.75)" d="M16 11c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 3-1.34 3-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        <text class="stat-value" x="32" y="24">{followers}</text>
        <text class="stat-label" x="32" y="38">Followers</text>
    </g>

    <!-- Metric 4: Forks -->
    <g transform="translate(393, 102)">
        <rect class="badge-bg" width="107" height="46"/>
        <path fill="#10b981" transform="translate(10, 14) scale(0.75)" d="M6 2a3 3 0 0 0-3 3v2a3 3 0 0 0 2 2.83V14a3 3 0 0 0 2 2.83V19a3 3 0 1 0 2 0v-2.17A3 3 0 0 0 11 14v-4.17A3 3 0 0 0 13 7V5a3 3 0 0 0-3-3 3 3 0 0 0-4 0z"/>
        <text class="stat-value" x="32" y="24">{total_forks}</text>
        <text class="stat-label" x="32" y="38">Forks</text>
    </g>

    <!-- Top Languages Progress Bar -->
    <g transform="translate(40, 168)">
        <text class="section-label" x="0" y="0">Top Languages</text>
        <g transform="translate(0, 12)" clip-path="url(#bar-clip)">
            {progress_bar_markup}
        </g>
    </g>

    <!-- Language Legend -->
    {legend_markup}

    <!-- Watermark / GitHub DevCard badge -->
    <g transform="translate(432, 238)">
        <text font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="9" font-weight="600" fill="{theme['subtitle']}" opacity="0.7">⚡ DevCard</text>
    </g>
</svg>'''
    return svg.strip()


def get_sample_stats() -> Dict[str, Any]:
    """Sample stats for instant preview without OAuth credentials."""
    return {
        "username": "octocat",
        "name": "Mona Lisa Octocat",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
        "bio": "Building the future of open source software & developer tools.",
        "location": "San Francisco, CA",
        "company": "@github",
        "public_repos": 42,
        "followers": 1337,
        "following": 9,
        "total_stars": 829,
        "total_forks": 142,
        "languages": [
            {"name": "TypeScript", "count": 18, "percentage": 42.8, "color": "#3178c6"},
            {"name": "Python", "count": 12, "percentage": 28.5, "color": "#3572A5"},
            {"name": "Rust", "count": 8, "percentage": 19.0, "color": "#dea584"},
            {"name": "Go", "count": 4, "percentage": 9.7, "color": "#00ADD8"},
        ],
        "created_year": "2011",
    }
