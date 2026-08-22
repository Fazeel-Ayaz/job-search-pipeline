#!/usr/bin/env python3
"""
job_scanner.py — Multi-source job scanner for lifecycle/CRM/retention roles.

Sources (10 active):
  Free, no key: Remotive, Greenhouse (direct), Lever (direct),
                SmartRecruiters (direct), Landing.jobs (EU),
                Relocate.me (international/visa roles),
                VisaSponsor.jobs (visa-sponsored EU+UK roles, HTML scrape)
  API key required: Adzuna (12 countries)
  RapidAPI (optional): JSearch (aggregates Google Jobs/LinkedIn/Indeed/Glassdoor)
  MCP integration: Indeed (pre-fetched via --indeed-file)

Pre-filters results using keyword and title rules from CLAUDE.md profile.
Deduplicates against scanned_history.json.
Outputs a clean JSON array to stdout.

Usage:
    python3 job_scanner.py                   # scan all sources, default 14 days
    python3 job_scanner.py --max-age 7       # only jobs from last 7 days
    python3 job_scanner.py --debug           # verbose logging to stderr
    python3 job_scanner.py --skip-rapidapi   # skip JSearch (save rate limit)
    python3 job_scanner.py --relocation-only # alias: all sources still run; relocation flag noted
    python3 job_scanner.py --indeed-file X   # ingest Indeed MCP results from JSON file

Reads API keys from ~/.claude-job-profile.json under "apis":
    apis.adzuna_app_id, apis.adzuna_app_key
    apis.rapidapi_key  (covers JSearch via RapidAPI)
"""

import json
import hashlib
import re
import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, quote_plus
from urllib.request import Request, urlopen

# ── Constants ─────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_PATH = BASE_DIR / "claude-job-profile.json"
HISTORY_PATH = BASE_DIR / "scanned_history.json"

MAX_PAGES = 3
ADZUNA_PER_PAGE = 50
DEFAULT_MAX_AGE = 14

# Adzuna country codes for target geography
ADZUNA_COUNTRIES = {
    "gb": "United Kingdom",
    "de": "Germany",
    "nl": "Netherlands",
    "be": "Belgium",
    "fr": "France",
    "se": "Sweden",
    "at": "Austria",
    "fi": "Finland",
    "ee": "Estonia",
    "lt": "Lithuania",
    "lu": "Luxembourg",
    "us": "United States",
    "au": "Australia",
    "sg": "Singapore",
    # "ae" removed — Adzuna returns 404 for all UAE queries
}

# ── Title-level keyword filters (applied before Claude scores) ────────

# At least one must appear in title OR snippet for the role to pass
INCLUDE_KEYWORDS = [
    # Lifecycle / CRM core
    "lifecycle", "life cycle", "crm", "retention", "reactivation",
    "activation", "churn", "engagement", "loyalty",
    "growth marketing", "user growth",
    "email marketing", "push notification",
    "braze", "moengage", "iterable", "clevertap", "customer.io",
    "subscription", "freemium", "membership",
    "cohort", "segmentation", "ltv", "lifetime value",
    "a/b test", "experimentation", "incrementality",
    "onboarding", "funnel", "conversion rate",
    "product marketing manager", "pmm",
    # Grocery / retail / new verticals domain signals
    "grocery", "quick commerce", "q-commerce", "new verticals",
    "supermarket", "convenience", "instant delivery",
    # Growth strategy / operations (catches Uber One / DH Growth Strategy style roles)
    "growth strategy",
    "cross-sell", "cross sell",
    "membership operations",
    "market launch",
    "go-to-market",
    "new market",
    "mau",
    "playbook",
    "rides-to-eats", "r2e",
    # Growth strategy & analytics (GROWTH-STRAT archetype — Agoda-type roles)
    "growth analytics",
    "marketing strategy",
    "commercial growth",
    "commercial strategy",
    "growth intelligence",
    "unit economics",
    "experimentation roadmap",
    "business impact",
    "p&l",
    "revenue management",
]

# Hard-exclude: if title contains any of these, skip immediately
EXCLUDE_TITLE_KEYWORDS = [
    "sales manager", "sales director", "sales executive", "sales lead",
    "business development", "account manager", "account executive",
    "account director", "key account",
    "media buyer", "media buying", "media planner",
    "performance marketing manager",  # only when it's the full title
    "seo manager", "seo specialist", "seo lead",
    "pr manager", "public relations",
    "brand manager",  # standalone brand roles
    "copywriter", "content writer",
    "frontend", "front-end", "backend", "back-end", "full stack",
    "software engineer", "data engineer", "devops",
    "product designer", "ux designer", "ui designer",
    "recruiter", "talent acquisition",
    "finance manager", "financial analyst",
    "supply chain", "logistics",
    "restaurant manager", "partner manager",
]

# Search queries for Adzuna and Reed
SEARCH_QUERIES = [
    # Growth marketing — standalone (no CRM qualifier)
    "growth marketing manager",
    "senior growth marketing manager",
    "head of growth marketing",
    "growth marketing lead",
    "user growth manager",
    "growth manager consumer",
    # Product marketing manager (PMM)
    "product marketing manager consumer",
    "product marketing manager app",
    "senior product marketing manager",
    "product marketing lead consumer",
    # Growth strategy / operations
    "growth strategy manager",
    "growth operations manager",
    "subscription growth manager",
    "membership growth manager",
    # CRM / lifecycle (trimmed)
    "lifecycle marketing manager",
    "CRM marketing manager",
    "retention marketing manager",
    "lifecycle CRM manager",
    # Domain-specific growth
    "growth marketing manager grocery",
    "growth marketing manager marketplace",
    "growth marketing manager fintech",
    "growth marketing manager subscription",
    "growth manager new verticals",
    "quick commerce growth manager",
    # Head-of level
    "head of growth",
    "head of marketing growth",
    # Growth strategy & analytics (GROWTH-STRAT archetype — Agoda-type roles)
    "marketing growth strategy",
    "growth strategy analytics",
    "growth analytics manager",
    "commercial growth manager",
    "marketing strategy manager",
    "growth intelligence manager",
    "commercial strategy manager",
]

# ── JSearch (RapidAPI) ───────────────────────────────────────────────
# Natural-language "role in location" queries — JSearch handles multi-board
# aggregation (Google Jobs, LinkedIn, Indeed, Glassdoor, ZipRecruiter).
# Free tier: 500 req/month. Keep to ~20 queries per run (4 runs/month = 80 req).
JSEARCH_QUERIES = [
    "growth marketing manager in London",
    "growth marketing manager in Berlin",
    "senior growth marketing manager in Amsterdam",
    "user growth manager in Europe",
    "head of growth marketing in Europe",
    "product marketing manager consumer in London",
    "senior product marketing manager in Berlin",
    "product marketing manager app in Europe",
    "product marketing manager marketplace Europe",
    "lifecycle marketing manager in London",
    "CRM manager lifecycle in London",
    "retention marketing manager in Europe",
    "growth strategy manager Europe",
    "subscription growth manager Europe",
    "membership growth manager London",
    # Location-specific queries are appended dynamically from personal.location in profile
    # (see get_location_queries() and scan_jsearch())
    "growth marketing manager remote Europe",
    "product marketing manager remote Europe",
    # Growth strategy & analytics (GROWTH-STRAT archetype)
    "marketing growth strategy analytics Europe",
    "growth analytics manager in London",
    "growth analytics manager in Berlin",
    "commercial growth manager in Europe",
    "marketing strategy manager consumer tech",
    "growth intelligence manager Europe",
    "growth manager consumer tech Europe",
]

JSEARCH_HOST = "jsearch.p.rapidapi.com"


def get_location_queries(profile):
    """Build location-specific JSearch queries from personal.location in profile JSON."""
    location = profile.get("personal", {}).get("location", "")
    if not location or location.startswith("YOUR_"):
        return []
    city = location.split(",")[0].strip()
    return [
        f"growth marketing manager in {city}",
        f"product marketing manager in {city}",
        f"lifecycle marketing manager in {city}",
    ]

# ── Greenhouse / Lever direct company endpoints (no API key needed) ───
# These ATS platforms expose public job feeds for each company.
# Add or remove companies here — slugs are the subdomain/path used by each company.
# Greenhouse slugs — verified live 2026-05-30 (404 = company not on GH)
# To find a slug: go to company's careers page, look for boards.greenhouse.io in the URL
# Add new slugs here as you discover them — 404s are handled gracefully
GREENHOUSE_COMPANIES = [
    # Confirmed active
    "wolt",         # Wolt — food delivery
    "hellofresh",   # HelloFresh — meal kits
    "airbnb",       # Airbnb — travel
    "instacart",    # Instacart — grocery delivery
    "nubank",       # Nubank — fintech
    "chime",        # Chime — fintech
    "monzo",        # Monzo — fintech
    "duolingo",     # Duolingo — edtech
    "n26",          # N26 — fintech
    "skyscanner",   # Skyscanner — travel
    "calm",         # Calm — wellness
    "kayak",        # KAYAK — travel
    # Growth / PMM companies added
    "depop",        # Depop — fashion marketplace
    "bumble",       # Bumble — social/dating
    "headspace",    # Headspace — wellness
    "deezer",       # Deezer — music streaming
    "indriver",     # inDrive — mobility
    "grab",         # Grab — super app
    "agoda",        # Agoda — travel (Booking Holdings)
    "bookingcom",   # Booking.com — travel (Booking Holdings)
]

# Lever slugs — verified live 2026-05-30
# To find a slug: look for jobs.lever.co/{slug} on the company's careers page
LEVER_COMPANIES = [
    # Confirmed active
    "spotify",      # Spotify — music/streaming
    "bolt-eu",      # Bolt — mobility/delivery
    "deliveroo",    # Deliveroo — food delivery
]

# Display names for company slugs — fallback is slug.replace("-", " ").title()
COMPANY_DISPLAY_NAMES = {
    "deliveryhero": "Delivery Hero",
    "hellofresh": "HelloFresh",
    "doordash": "DoorDash",
    "nekohealth": "Neko Health",
    "simpleclub": "simpleclub",
    "indriver": "inDrive",
    "justeattakeaway": "Just Eat Takeaway",
    "justetakeaway": "Just Eat Takeaway",
    "bookingcom": "Booking.com",
    "booking": "Booking.com",
    "n26": "N26",
    "klarna": "Klarna",
    "getir": "Getir",
    "gorillas": "Gorillas",
    "gojek": "Gojek",
}

# ── SmartRecruiters per-company API ──────────────────────────────────
# SmartRecruiters exposes a public job board API — no auth required.
# URL: https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100
# Slug = company identifier visible in SmartRecruiters job URLs.
# Verified slugs 2026-06-03. Add new ones as you spot SmartRecruiters job URLs.
SMARTRECRUITERS_COMPANIES = [
    # (slug, display_name)
    # Food delivery / mobility
    ("DeliveryHero",       "Delivery Hero"),
    ("Careem",             "Careem"),
    ("GlovoApp",           "Glovo"),
    # Fintech
    ("Klarna",             "Klarna"),
    ("Remitly",            "Remitly"),
    # Consumer tech / marketplaces
    ("Vinted",             "Vinted"),
    ("ASOS",               "ASOS"),
    ("Zalando",            "Zalando"),
    ("HelloFreshGroup",    "HelloFresh"),
    # Travel
    ("Booking.com",        "Booking.com"),
    ("ExpediaGroup",       "Expedia"),
]


_debug = False

log = logging.getLogger("scanner")

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

ADZUNA_WORKERS = 8
SOURCE_WORKERS = 6


def _make_request(url, accept="application/json", extra_headers=None):
    """Build a Request with the default User-Agent. Override headers via extra_headers dict."""
    headers = {"Accept": accept, "User-Agent": DEFAULT_UA}
    if extra_headers:
        headers.update(extra_headers)
    return Request(url, headers=headers)


# ── Profile loading ───────────────────────────────────────────────────

def load_profile():
    """Load profile from ~/.claude-job-profile.json"""
    if not PROFILE_PATH.exists():
        print("[scanner] ERROR: ~/.claude-job-profile.json not found", file=sys.stderr)
        sys.exit(1)
    return json.loads(PROFILE_PATH.read_text())


def get_api_keys(profile):
    """Extract API keys from profile"""
    apis = profile.get("apis", {})
    return {
        "adzuna_app_id": apis.get("adzuna_app_id", ""),
        "adzuna_app_key": apis.get("adzuna_app_key", ""),
        "rapidapi_key": apis.get("rapidapi_key", ""),
    }


def get_target_companies(profile):
    """Get lowercase set of target company names"""
    return {c.lower().strip() for c in profile.get("target_companies", [])}


def get_recently_applied(profile):
    """Get set of (company_lower, role_lower) tuples already applied to"""
    applied = set()
    for entry in profile.get("recently_applied", []):
        company = entry.get("company", "").lower().strip()
        role = entry.get("role", "").lower().strip()
        if company:
            applied.add((company, role))
    return applied


# ── Dedup history ─────────────────────────────────────────────────────

def load_history():
    """Load scanned_history.json: {hash: {title, company, date_first_seen}}"""
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_history(history):
    """Save scanned_history.json"""
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def dedup_key(company, title):
    """Generate a hash key from company + title for dedup"""
    raw = f"{company.lower().strip()}|{title.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


# ── Pre-filter logic ─────────────────────────────────────────────────

def passes_title_filter(title):
    """Returns False if title matches any hard-exclude keyword"""
    lower = title.lower()
    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in lower:
            return False
    return True


def passes_include_filter(title, snippet, target_companies, company, strict=False):
    """
    Returns True if:
    - title or snippet contains at least one include keyword, OR
    - company is in the target companies list AND strict=False

    strict=True: keyword match always required (used for per-company job board sources
    like Greenhouse, Lever, SmartRecruiters where we fetch ALL jobs, not just keyword hits).
    strict=False: target company match bypasses keyword requirement (used for aggregators
    like Adzuna/Reed where a role at Wolt might not mention 'lifecycle' in the snippet).
    """
    # Check title and snippet for include keywords (always applied)
    combined = f"{title} {snippet}".lower()
    for kw in INCLUDE_KEYWORDS:
        if kw in combined:
            return True

    # For aggregator sources only: also pass through if company is a target company
    if not strict:
        company_lower = company.lower().strip()
        for tc in target_companies:
            if tc in company_lower or company_lower in tc:
                return True

    return False


def get_in_pipeline_companies(profile):
    """
    Query Notion live for companies in active interview stages.
    Only these are blocked from re-scanning — Applied/Rejected/Withdrawn are fair game.

    Active statuses: Interview Scheduled, Round 2, Round 3+, Offer
    Falls back to empty set if Notion is unavailable so the scan never hard-fails.
    """
    try:
        token = profile.get("apis", {}).get("notion_token", "")
        db_id = profile.get("notion", {}).get("database_id", "")
        if not token or not db_id:
            log.debug("[pipeline] No Notion token/db_id — skipping pipeline block")
            return set()

        NOTION_VER  = "2022-06-28"
        NOTION_BASE = "https://api.notion.com/v1"
        active      = ["Interview Scheduled", "Round 2", "Round 3+", "Offer"]

        filter_body = {
            "filter": {"or": [{"property": "Status", "select": {"equals": s}} for s in active]},
            "page_size": 100,
        }
        companies, cursor = set(), None
        while True:
            body = dict(filter_body)
            if cursor:
                body["start_cursor"] = cursor
            req = Request(
                f"{NOTION_BASE}/databases/{db_id}/query",
                data=json.dumps(body).encode(),
                method="POST",
                headers={
                    "Authorization":  f"Bearer {token}",
                    "Notion-Version": NOTION_VER,
                    "Content-Type":   "application/json",
                },
            )
            with urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
            for page in result.get("results", []):
                co = "".join(
                    seg.get("plain_text", "")
                    for seg in page.get("properties", {}).get("Company", {}).get("rich_text", [])
                ).lower().strip()
                if co:
                    companies.add(co)
            if not result.get("has_more"):
                break
            cursor = result.get("next_cursor")

        if companies:
            log.info("[pipeline] Blocking %d companies in active interview: %s",
                     len(companies), ", ".join(sorted(companies)))
        else:
            log.info("[pipeline] No companies in active interview — no pipeline blocks")
        return companies

    except Exception as exc:
        log.warning("[pipeline] Notion query failed (%s) — proceeding without pipeline block", exc)
        return set()


def is_in_active_pipeline(company, in_pipeline):
    """Return True only if the company is currently in an active interview stage."""
    company_lower = company.lower().strip()
    for pipeline_co in in_pipeline:
        if pipeline_co in company_lower or company_lower in pipeline_co:
            return True
    return False


# ── Date helpers ──────────────────────────────────────────────────────

def age_days_from_iso(created):
    """Calculate age in days from ISO date string"""
    if not created:
        return None
    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        return None


def age_days_from_relative(text):
    """Parse relative age strings like '2d ago', '1w ago'"""
    if not text:
        return None
    text = text.strip().lower()
    m = re.match(r'(\d+)\s*(m|h|d|w|mo)\s*ago', text)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    if unit in ('m', 'h'):
        return 0
    if unit == 'd':
        return n
    if unit == 'w':
        return n * 7
    if unit == 'mo':
        return n * 30
    return None


# ── Adzuna API ────────────────────────────────────────────────────────

def fetch_adzuna_page(country_code, app_id, app_key, query, max_age, page):
    """Fetch one page of Adzuna results"""
    params = urlencode({
        "app_id": app_id,
        "app_key": app_key,
        "what": query,
        "max_days_old": max_age,
        "results_per_page": ADZUNA_PER_PAGE,
        "sort_by": "date",
    })
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}?{params}"
    log.debug("[adzuna] GET %s", url)

    req = _make_request(url)
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except (URLError, HTTPError, OSError, ValueError) as e:
        log.debug("[adzuna] error: %s", e)
        return {}


def _adzuna_country_query(country_code, country_name, query, app_id, app_key, max_age):
    """Fetch all pages for one country+query combo. Returns list of job dicts."""
    jobs = []
    for page in range(1, MAX_PAGES + 1):
        data = fetch_adzuna_page(country_code, app_id, app_key, query, max_age, page)
        if "exception" in data:
            log.debug("[adzuna] API error %s/%s: %s", country_code, query, data["exception"])
            break
        results = data.get("results", [])
        if not results:
            break
        for j in results:
            url = (j.get("redirect_url") or "").strip()
            title = (j.get("title") or "").strip()
            company = (j.get("company") or {}).get("display_name", "").strip()
            location = (j.get("location") or {}).get("display_name", "").strip()
            snippet = (j.get("description") or "").strip()[:300]
            created = j.get("created", "")
            jobs.append({
                "title": title,
                "company": company,
                "location": f"{location}, {country_name}" if location else country_name,
                "url": url,
                "source": "adzuna",
                "snippet": snippet,
                "age_days": age_days_from_iso(created),
                "_url_key": re.sub(r'\?.*$', '', url),
            })
        total_available = data.get("count", 0)
        if len(results) < ADZUNA_PER_PAGE or page * ADZUNA_PER_PAGE >= total_available:
            break
    return jobs


def scan_adzuna(app_id, app_key, max_age):
    """Scan Adzuna across all target countries and queries (parallelized)."""
    if not app_id or not app_key:
        log.info("[adzuna] SKIP: no API keys configured")
        return []

    tasks = []
    for country_code, country_name in ADZUNA_COUNTRIES.items():
        for query in SEARCH_QUERIES:
            tasks.append((country_code, country_name, query))

    all_jobs = []
    seen_urls = set()
    done = 0

    with ThreadPoolExecutor(max_workers=ADZUNA_WORKERS) as pool:
        futures = {
            pool.submit(_adzuna_country_query, cc, cn, q, app_id, app_key, max_age): (cc, q)
            for cc, cn, q in tasks
        }
        for future in as_completed(futures):
            cc, q = futures[future]
            done += 1
            try:
                jobs = future.result()
                for j in jobs:
                    url_key = j.pop("_url_key")
                    if url_key not in seen_urls:
                        seen_urls.add(url_key)
                        all_jobs.append(j)
            except Exception as e:
                log.warning("[adzuna] %s/%s failed: %s", cc, q, e)
            if done % 50 == 0 or done == len(tasks):
                log.info("[adzuna] %d/%d combos done, %d jobs so far", done, len(tasks), len(all_jobs))

    log.info("[adzuna] DONE: %d raw jobs across %d countries", len(all_jobs), len(ADZUNA_COUNTRIES))
    return all_jobs


# ── JSearch (RapidAPI) ───────────────────────────────────────────────

def _rapidapi_get(url, params, host, api_key):
    """Generic RapidAPI GET helper — returns parsed JSON or {}"""
    qs = urlencode(params)
    req = _make_request(
        f"{url}?{qs}",
        extra_headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host,
        }
    )
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        if e.code == 429:
            log.warning("[rapidapi] Rate limit hit on %s", host)
        elif e.code == 403:
            log.warning("[rapidapi] 403 Forbidden — check subscription for %s", host)
        else:
            log.debug("[rapidapi] HTTP %d for %s", e.code, url)
        return {}
    except (URLError, OSError, ValueError) as e:
        log.debug("[rapidapi] Connection error: %s", e)
        return {}


def scan_jsearch(api_key, max_age, profile=None):
    """
    Scan JSearch (RapidAPI) — aggregates Google Jobs, LinkedIn, Indeed, Glassdoor.
    Endpoint: GET https://jsearch.p.rapidapi.com/search
    Free tier: 500 req/month. Each query = 1 request (num_pages=1).
    """
    if not api_key:
        log.info("[jsearch] SKIP: no rapidapi_key in profile")
        return []

    # date_posted param: "week" covers ~7 days, "month" covers ~30 days
    date_posted = "month" if max_age >= 20 else "week"

    queries = JSEARCH_QUERIES + get_location_queries(profile or {})

    all_jobs = []
    seen_ids = set()

    for query in queries:
        data = _rapidapi_get(
            "https://jsearch.p.rapidapi.com/search",
            {
                "query": query,
                "page": "1",
                "num_pages": "1",
                "date_posted": date_posted,
                "employment_type": "FULLTIME",
                "actively_hiring": "true",
            },
            JSEARCH_HOST,
            api_key,
        )

        results = data.get("data", [])
        if not results:
            log.debug("[jsearch] 0 results for: %s", query)
            continue

        new = 0
        for j in results:
            job_id = j.get("job_id", "")
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = (j.get("job_title") or "").strip()
            company = (j.get("employer_name") or "").strip()
            city = j.get("job_city") or ""
            country = j.get("job_country") or ""
            location = ", ".join(filter(None, [city, country]))
            apply_url = (j.get("job_apply_link") or j.get("job_google_link") or "").strip()
            description = (j.get("job_description") or "").strip()[:400]
            posted_at = j.get("job_posted_at_datetime_utc", "")
            age = age_days_from_iso(posted_at)
            is_remote = j.get("job_is_remote", False)
            if is_remote and not location:
                location = "Remote"

            all_jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": apply_url,
                "source": "jsearch",
                "snippet": description,
                "age_days": age,
            })
            new += 1

        log.debug("[jsearch] '%s': %d new jobs", query[:50], new)

    log.info("[jsearch] DONE: %d raw jobs across %d queries", len(all_jobs), len(queries))
    return all_jobs


# ── Remotive API ──────────────────────────────────────────────────────

def scan_remotive():
    """
    Scan Remotive public API — remote tech/startup roles globally, no key needed.
    Endpoint: https://remotive.com/api/remote-jobs
    """
    all_jobs = []

    for category in ["marketing", "product"]:
        url = f"https://remotive.com/api/remote-jobs?category={category}&limit=100"
        log.debug("[remotive] GET %s", url)

        req = _make_request(url)
        try:
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except (URLError, HTTPError, OSError, ValueError) as e:
            log.debug("[remotive] error: %s", e)
            continue

        for j in data.get("jobs", []):
            job_url = (j.get("url") or "").strip()
            if not job_url:
                continue

            title = (j.get("title") or "").strip()
            company = (j.get("company_name") or "").strip()
            location = (j.get("candidate_required_location") or "Remote").strip()
            snippet = re.sub(r'<[^>]+>', '', (j.get("description") or ""))[:300]
            published = j.get("publication_date", "")
            age = age_days_from_iso(published)

            all_jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "source": "remotive",
                "snippet": snippet,
                "age_days": age,
            })

    log.info("[remotive] DONE: %d raw jobs", len(all_jobs))
    return all_jobs


# ── Greenhouse per-company API ────────────────────────────────────────

def scan_greenhouse():
    """
    Scan Greenhouse public job boards for each target company.
    No API key required — public endpoint.
    Official URL: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
    Returns all current openings for the company. 404 = company not on Greenhouse, skip silently.
    """
    all_jobs = []
    seen_ids = set()
    found_companies = 0

    for slug in GREENHOUSE_COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
        log.debug("[greenhouse] GET %s", url)

        req = _make_request(url)
        try:
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            if e.code != 404:
                log.debug("[greenhouse] %s: HTTP %d", slug, e.code)
            continue
        except (URLError, OSError, ValueError) as e:
            log.debug("[greenhouse] %s: %s", slug, e)
            continue

        jobs_for_slug = data.get("jobs", [])
        if not jobs_for_slug:
            continue
        found_companies += 1
        display_name = COMPANY_DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())

        for j in jobs_for_slug:
            job_id = j.get("id", "")
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = (j.get("title") or "").strip()
            offices = j.get("offices", [{}])
            location = offices[0].get("name", "") if offices else ""
            job_url = (j.get("absolute_url") or "").strip()
            # content field contains HTML — strip tags for snippet
            snippet = re.sub(r'<[^>]+>', ' ', (j.get("content") or ""))
            snippet = re.sub(r'\s+', ' ', snippet).strip()[:300]
            # updated_at format: "2024-01-15T10:30:00.000Z"
            updated = j.get("updated_at", "")
            age = age_days_from_iso(updated)

            all_jobs.append({
                "title": title,
                "company": display_name,
                "location": location,
                "url": job_url,
                "source": f"greenhouse/{slug}",
                "snippet": snippet,
                "age_days": age,
            })

    log.info("[greenhouse] DONE: %d jobs from %d/%d companies", len(all_jobs), found_companies, len(GREENHOUSE_COMPANIES))
    return all_jobs


# ── Lever per-company API ─────────────────────────────────────────────

def scan_lever():
    """
    Scan Lever public job postings for each target company.
    No API key required — public endpoint.
    URL: https://api.lever.co/v0/postings/{slug}?mode=json
    Returns a JSON array. Empty array or 404 = company not on Lever, skip silently.
    Field reference: text (title), hostedUrl, categories.location, categories.team,
                     descriptionPlain (plain text), description (HTML), createdAt (ms timestamp)
    """
    all_jobs = []
    seen_ids = set()
    found_companies = 0

    for slug in LEVER_COMPANIES:
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        log.debug("[lever] GET %s", url)

        req = _make_request(url)
        try:
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            if e.code != 404:
                log.debug("[lever] %s: HTTP %d", slug, e.code)
            continue
        except (URLError, OSError, ValueError) as e:
            log.debug("[lever] %s: %s", slug, e)
            continue

        postings = data if isinstance(data, list) else []
        if not postings:
            continue
        found_companies += 1
        display_name = COMPANY_DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())

        for j in postings:
            job_id = j.get("id", "")
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = (j.get("text") or "").strip()
            categories = j.get("categories", {})
            location = (categories.get("location") or categories.get("allLocations", [""])[0] if isinstance(categories.get("allLocations"), list) else "").strip()
            team = (categories.get("team") or "").strip()
            job_url = (j.get("hostedUrl") or j.get("applyUrl") or "").strip()

            # descriptionPlain = plain text; fall back to stripping description HTML
            raw_desc = j.get("descriptionPlain") or re.sub(r'<[^>]+>', ' ', j.get("description") or "")
            snippet = re.sub(r'\s+', ' ', raw_desc).strip()[:300]
            if team and not snippet.startswith(f"[{team}]"):
                snippet = f"[{team}] {snippet}"

            # createdAt is a Unix timestamp in milliseconds
            posted_at = j.get("createdAt", 0)
            age = None
            if posted_at:
                try:
                    dt = datetime.fromtimestamp(int(posted_at) / 1000, tz=timezone.utc)
                    age = max(0, (datetime.now(timezone.utc) - dt).days)
                except Exception:
                    pass

            all_jobs.append({
                "title": title,
                "company": display_name,
                "location": location,
                "url": job_url,
                "source": f"lever/{slug}",
                "snippet": snippet,
                "age_days": age,
            })

    log.info("[lever] DONE: %d jobs from %d/%d companies", len(all_jobs), found_companies, len(LEVER_COMPANIES))
    return all_jobs


# ── SmartRecruiters per-company API ──────────────────────────────────

def scan_smartrecruiters():
    """
    Scan SmartRecruiters public job board API for each target company.
    No API key required — public endpoint.
    URL: https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100
    Returns all current openings. 404 = company not on SmartRecruiters, skip silently.
    """
    all_jobs = []
    seen_ids = set()
    found_companies = 0

    for slug, display_name in SMARTRECRUITERS_COMPANIES:
        offset = 0
        company_jobs = []

        while True:
            url = (f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
                   f"?limit=100&offset={offset}")
            log.debug("[smartrecruiters] GET %s", url)

            req = _make_request(url)
            try:
                with urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read())
            except HTTPError as e:
                if e.code != 404:
                    log.debug("[smartrecruiters] %s: HTTP %d", slug, e.code)
                break
            except (URLError, OSError, ValueError) as e:
                log.debug("[smartrecruiters] %s: %s", slug, e)
                break

            postings = data.get("content", [])
            if not postings:
                break

            for j in postings:
                job_id = j.get("id", "")
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = (j.get("name") or "").strip()
                loc = j.get("location", {})
                city = loc.get("city", "")
                country = loc.get("country", "")
                remote = loc.get("remote", False)
                location = ", ".join(filter(None, [city, country]))
                if remote and not location:
                    location = "Remote"

                # SmartRecruiters job URL pattern
                job_url = j.get("ref", f"https://jobs.smartrecruiters.com/{slug}/{job_id}")

                # Snippet from jobAd sections if available
                job_ad = j.get("jobAd", {})
                sections = job_ad.get("sections", {})
                desc_html = (sections.get("jobDescription", {}).get("text", "") or
                             sections.get("companyDescription", {}).get("text", ""))
                snippet = re.sub(r'<[^>]+>', ' ', desc_html)
                snippet = re.sub(r'\s+', ' ', snippet).strip()[:300]

                # Released date for age calculation
                released = j.get("releasedDate", "")
                age = age_days_from_iso(released)

                company_jobs.append({
                    "title": title,
                    "company": display_name,
                    "location": location,
                    "url": job_url,
                    "source": f"smartrecruiters/{slug}",
                    "snippet": snippet,
                    "age_days": age,
                })

            total = data.get("totalFound", 0)
            offset += len(postings)
            if offset >= total or len(postings) < 100:
                break

        if company_jobs:
            found_companies += 1
            all_jobs.extend(company_jobs)
            log.debug("[smartrecruiters] %s: %d jobs", slug, len(company_jobs))

    log.info("[smartrecruiters] DONE: %d jobs from %d/%d companies", len(all_jobs), found_companies, len(SMARTRECRUITERS_COMPANIES))
    return all_jobs


# ── Landing.jobs API ─────────────────────────────────────────────────
# Public endpoint — no auth required for job listings.
# Key field: relocation_paid (bool). Filter to EU country codes only.
# Docs: https://github.com/LandingJobs/LandingJobs-api
# Pagination: ?limit=50&offset=N

LANDING_JOBS_EU_COUNTRIES = {
    "DE", "NL", "GB", "BE", "FR", "SE", "AT", "FI", "EE", "LT", "LU",
    "PT", "ES", "PL", "IE", "DK", "CZ", "HU", "RO", "HR", "SI", "SK",
    "BG", "GR", "CY", "MT", "LV", "NO", "CH",
}

def scan_landing_jobs(max_age):
    """
    Scan Landing.jobs public API for EU roles with relocation support.
    Filters to relocation_paid=true and EU country codes.
    No API key required.
    """
    all_jobs = []
    seen_ids = set()
    offset = 0
    limit = 50
    pages_fetched = 0
    max_pages = 6  # 300 jobs max per run

    while pages_fetched < max_pages:
        url = f"https://landing.jobs/api/v1/jobs?limit={limit}&offset={offset}"
        log.debug("[landing.jobs] GET %s", url)

        req = _make_request(url)
        try:
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except (URLError, HTTPError, OSError, ValueError) as e:
            log.warning("[landing.jobs] error: %s", e)
            break

        # API returns a list directly (not wrapped in a key)
        results = data if isinstance(data, list) else []
        if not results:
            break

        for j in results:
            job_id = j.get("id")
            if not job_id or job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = (j.get("title") or "").strip()

            # Company name: not a direct field; extract from URL path
            # URL pattern: https://landing.jobs/at/{company-slug}/...
            raw_url = (j.get("url") or "").strip()
            company_name = ""
            if "/at/" in raw_url:
                slug = raw_url.split("/at/")[1].split("/")[0]
                company_name = slug.replace("-", " ").title()

            # Location: new API uses 'locations' array of {city, country_code}
            locations_arr = j.get("locations", [])
            city = ""
            country_code = ""
            if locations_arr and isinstance(locations_arr, list):
                loc0 = locations_arr[0]
                city = (loc0.get("city") or "").strip()
                country_code = (loc0.get("country_code") or "").upper()
            else:
                # Fallback to legacy flat fields
                city = (j.get("city") or "").strip()
                country_code = (j.get("country_code") or "").upper()
            country_name = (j.get("country_name") or country_code).strip()
            location = ", ".join(filter(None, [city, country_name]))

            # Landing.jobs is an EU-focused board — accept all jobs from the API.
            # If country_code is set and NOT in our EU list, skip.
            # If country_code is missing, accept the job.
            if country_code and country_code not in LANDING_JOBS_EU_COUNTRIES:
                continue

            # Check relocation flags
            relocation_paid = j.get("relocation_paid", False)
            relocation_assistance = j.get("relocation_assistance", False)

            # Use the actual URL from the API if available, else construct from ID
            job_url = raw_url or f"https://landing.jobs/jobs/{job_id}"

            snippet_parts = []
            if j.get("role_description"):
                snippet_parts.append(re.sub(r'<[^>]+>', ' ', j["role_description"])[:200])
            tags = j.get("tags", [])
            if tags:
                snippet_parts.append("Tags: " + ", ".join(tags[:8]))
            if relocation_paid:
                snippet_parts.append("✓ Relocation paid")
            elif relocation_assistance:
                snippet_parts.append("✓ Relocation assistance")
            snippet = " | ".join(snippet_parts)[:400]

            published = (j.get("published_at") or j.get("created_at") or "").strip()
            age = age_days_from_iso(published)
            if age is not None and age > max_age:
                continue

            all_jobs.append({
                "title": title,
                "company": company_name or str(job_id),
                "location": location or "EU",
                "url": job_url,
                "source": "landing.jobs",
                "snippet": snippet,
                "age_days": age,
                "relocation": bool(relocation_paid or relocation_assistance),
            })

        offset += limit
        pages_fetched += 1

        # Stop if we got fewer results than a full page
        if len(results) < limit:
            break

    log.info("[landing.jobs] DONE: %d EU jobs", len(all_jobs))
    return all_jobs


# ── Relocate.me scraper ───────────────────────────────────────────────
# Relocate.me specifically curates tech jobs with visa sponsorship and
# relocation support for international candidates.
# No public API — fetches their JSON-LD structured data from the jobs listing.
# URL pattern: https://relocate.me/international-jobs?role=marketing&page=N

def scan_relocate_me(max_age):
    """
    Scrape Relocate.me for marketing/growth roles with relocation + visa support.
    Parses JSON-LD structured data embedded in listing pages.
    Falls back to basic HTML parsing if JSON-LD unavailable.
    """
    all_jobs = []
    seen_urls = set()

    search_roles = ["marketing", "product", "growth"]

    for role in search_roles:
        for page in range(1, 4):
            url = f"https://relocate.me/international-jobs?role={role}&page={page}"
            log.debug("[relocate.me] GET %s", url)

            req = _make_request(url, accept="text/html,application/xhtml+xml")

            try:
                with urlopen(req, timeout=25) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
            except (URLError, HTTPError, OSError, ValueError) as e:
                log.debug("[relocate.me] error for %s page %d: %s", role, page, e)
                break

            # Try parsing JSON-LD structured data first
            jobs_found = _parse_relocateme_jsonld(html, max_age, seen_urls)
            if not jobs_found:
                # Fall back to HTML card parsing
                jobs_found = _parse_relocateme_html(html, max_age, seen_urls)

            if not jobs_found:
                break  # No more results on this page

            all_jobs.extend(jobs_found)

    log.info("[relocate.me] DONE: %d jobs with relocation/visa support", len(all_jobs))
    return all_jobs


def _parse_relocateme_jsonld(html, max_age, seen_urls):
    """Extract jobs from JSON-LD JobPosting structured data blocks."""
    jobs = []
    # Find all JSON-LD script blocks
    ld_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    )
    for block in ld_blocks:
        try:
            data = json.loads(block.strip())
        except (json.JSONDecodeError, ValueError):
            continue

        # Handle both single object and @graph arrays
        items = []
        if isinstance(data, list):
            items = data
        elif data.get("@type") == "JobPosting":
            items = [data]
        elif "@graph" in data:
            items = data["@graph"]

        for item in items:
            if item.get("@type") != "JobPosting":
                continue

            title = (item.get("title") or item.get("name") or "").strip()
            company = (item.get("hiringOrganization") or {})
            if isinstance(company, dict):
                company = company.get("name", "")
            company = str(company).strip()

            # URL
            job_url = (item.get("url") or item.get("sameAs") or "").strip()
            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            # Location
            loc_obj = item.get("jobLocation") or {}
            if isinstance(loc_obj, list):
                loc_obj = loc_obj[0] if loc_obj else {}
            address = loc_obj.get("address", {})
            if isinstance(address, dict):
                city = address.get("addressLocality", "")
                country = address.get("addressCountry", "")
                location = ", ".join(filter(None, [city, country]))
            else:
                location = str(address)

            snippet = re.sub(r'<[^>]+>', ' ',
                             (item.get("description") or ""))[:300].strip()
            snippet = re.sub(r'\s+', ' ', snippet)
            if snippet:
                snippet += " | ✓ Relocation/visa support"

            date_posted = (item.get("datePosted") or "").strip()
            age = age_days_from_iso(date_posted)
            if age is not None and age > max_age:
                continue

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "source": "relocate.me",
                "snippet": snippet,
                "age_days": age,
                "relocation": True,
            })

    return jobs


def _parse_relocateme_html(html, max_age, seen_urls):
    """Parse job cards from Relocate.me listing HTML (updated for 2025/2026 markup).

    Current card structure:
        <div class="jobs-list__job [job_featured]">
            ...
            <a href="/{country}/{city}/{company}/{slug}"> (relative link)
            ...
            <div class="job__title">Title in Location</div>
            <div class="job__company ...">Location text</div>
            <div class="job__company ...">Company name</div>
            ...
        </div>
    """
    jobs = []

    # Split HTML into job cards using the card container class
    cards = re.findall(
        r'<div[^>]+class="jobs-list__job[^"]*"[^>]*>(.*?)(?=<div[^>]+class="jobs-list__job|<div class="jobs-list__heading)',
        html, re.DOTALL
    )

    for card in cards:
        # Extract the first href (the job detail link)
        href_m = re.search(r'href="(/[^"]+)"', card)
        if not href_m:
            continue
        relative_url = href_m.group(1)
        # Skip promotional/ad cards (e.g. /remote/remote/the-global-move/...)
        if "the-global-move" in relative_url:
            continue
        job_url = f"https://relocate.me{relative_url}"
        if job_url in seen_urls:
            continue
        seen_urls.add(job_url)

        # Extract title from job__title div
        title_m = re.search(r'class="job__title"[^>]*>(.*?)</(?:div|a|h\d)', card, re.DOTALL)
        if not title_m:
            continue
        title = re.sub(r'<[^>]+>', ' ', title_m.group(1))
        title = re.sub(r'\s+', ' ', title).strip()
        if not title:
            continue

        # Extract company and location from job__company divs
        # There are typically 2: first is location (with SVG map pin icon), second is company name
        company_divs = re.findall(
            r'class="job__company[^"]*"[^>]*>(.*?)</div>',
            card, re.DOTALL
        )
        company_texts = []
        for div_content in company_divs:
            text = re.sub(r'<[^>]+>', '', div_content).strip()
            if text:
                company_texts.append(text)

        # Parse location from the relative URL path: /{country}/{city}/{company}/{slug}
        path_parts = relative_url.strip('/').split('/')
        if len(path_parts) >= 3:
            country_name = path_parts[0].replace('-', ' ').title()
            city_name = path_parts[1].replace('-', ' ').title()
            company_slug = path_parts[2].replace('-', ' ').title()
            location = f"{city_name}, {country_name}"
        else:
            location = "Europe"
            company_slug = ""

        # Company: prefer the second job__company text, fall back to URL slug
        company = ""
        if len(company_texts) >= 2:
            company = company_texts[1]  # second div is typically the company name
        elif company_slug:
            company = company_slug

        # Remove " in City" from title if present (Relocate.me appends location)
        title = re.sub(r'\s+in\s+' + re.escape(city_name if len(path_parts) >= 3 else ''), '', title).strip()

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "source": "relocate.me",
            "snippet": "✓ Relocation/visa support",
            "age_days": None,
            "relocation": True,
        })

    return jobs


# ── VisaSponsor.jobs ──────────────────────────────────────────────────

# Target countries for visa sponsorship search (full names as used by the site)
VISASPONSOR_COUNTRIES = [
    "United-Kingdom",
    "Germany",
    "Netherlands",
    "Belgium",
    "France",
    "Sweden",
    "Finland",
    "Estonia",
    "Lithuania",
    "Luxembourg",
]

VISASPONSOR_CLASSIFICATIONS = ["Marketing-and-Media"]


def _parse_visasponsor_date(date_str):
    """Parse DD-MM-YYYY publish date → age in days from today."""
    if not date_str:
        return None
    m = re.match(r'(\d{2})-(\d{2})-(\d{4})', date_str.strip())
    if not m:
        return None
    try:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        posted = datetime(year, month, day, tzinfo=timezone.utc)
        return (datetime.now(tz=timezone.utc) - posted).days
    except ValueError:
        return None


def _parse_visasponsor_cards(html, max_age, seen_urls, country):
    """Parse job cards from a visasponsor.jobs listing page.

    Card structure (Bootstrap, server-side rendered):
        <a href="/api/jobs/{32-char-hash}/{slug}" class="col-12 col-lg-4" ...>
          <div class="fs-5 fw-medium mb-2 overflow-hidden">TITLE</div>
          <span class="...employer-name" ...>COMPANY</span>
          <div class="col-11 sub-font">
            <span style="color:#25201F">CITY, </span>
            <span style="color:#25201F">REGION, </span>
            <span style="color:#25201F">COUNTRY</span>
          </div>
          <div class="...tag sub-font" style="...color:green">VISA_TYPE</div>
          <span style="color:#7B8589">Publish date </span>
          <span style="color:#25201F">DD-MM-YYYY</span>
        </a>
    """
    jobs = []

    card_pattern = r'<a\s[^>]*href="(/api/jobs/[a-f0-9]{32}/[^"]+)"[^>]*class="col-12 col-lg-4"[^>]*>'
    card_starts = [(m.group(1), m.start()) for m in re.finditer(card_pattern, html)]

    for i, (href, start) in enumerate(card_starts):
        end = card_starts[i + 1][1] if i + 1 < len(card_starts) else len(html)
        card = html[start:end]

        job_url = "https://visasponsor.jobs" + href.replace("&amp;", "&")
        if job_url in seen_urls:
            continue
        seen_urls.add(job_url)

        # Title
        title_m = re.search(r'class="fs-5 fw-medium[^"]*"[^>]*>(.*?)</div>', card, re.DOTALL)
        if not title_m:
            continue
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
        title = title.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
        if not title:
            continue

        # Company
        company_m = re.search(r'class="[^"]*employer-name[^"]*"[^>]*>(.*?)</span>', card, re.DOTALL)
        company = re.sub(r'<[^>]+>', '', company_m.group(1)).strip() if company_m else ""

        # Location: spans inside <div class="col-11 sub-font">
        loc_m = re.search(r'class="col-11 sub-font">(.*?)</div>', card, re.DOTALL)
        location = country.replace("-", " ")
        if loc_m:
            parts = re.findall(r'style="color:#25201F">(.*?)</span>', loc_m.group(1))
            clean = [re.sub(r'<[^>]+>', '', p).strip().rstrip(',').strip() for p in parts if p.strip()]
            if clean:
                location = ", ".join(clean)

        # Publish date → age in days
        date_m = re.search(
            r'Publish date\s*</span>\s*<span[^>]*style="color:#25201F"[^>]*>(.*?)</span>', card
        )
        age = _parse_visasponsor_date(date_m.group(1).strip()) if date_m else None

        if age is not None and age > max_age:
            continue

        # Visa type badge
        visa_m = re.search(r'class="[^"]*tag sub-font"[^>]*color:green[^>]*>(.*?)</div>', card, re.DOTALL)
        visa_type = re.sub(r'<[^>]+>', '', visa_m.group(1)).strip() if visa_m else ""
        snippet = f"✓ Visa sponsorship ({visa_type})" if visa_type else "✓ Visa sponsorship"

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "source": "visasponsor",
            "snippet": snippet,
            "age_days": age,
            "relocation": True,
        })

    return jobs


def scan_visasponsor(max_age):
    """
    Scan visasponsor.jobs for visa-sponsored marketing roles in EU target countries.
    No API key needed; returns HTML pages paginated via page=0,1,2,...
    Treated as a relocation board — strict keyword filter applied.
    """
    all_jobs = []
    seen_urls = set()

    for country in VISASPONSOR_COUNTRIES:
        for classification in VISASPONSOR_CLASSIFICATIONS:
            for page in range(MAX_PAGES):
                url = (
                    f"https://visasponsor.jobs/api/jobs"
                    f"?country={country}&classification={classification}&page={page}"
                )
                log.debug("[visasponsor] GET %s", url)

                req = _make_request(url)
                try:
                    with urlopen(req, timeout=20) as resp:
                        html = resp.read().decode("utf-8", errors="replace")
                except (URLError, HTTPError, OSError) as e:
                    log.debug("[visasponsor] %s: %s", country, e)
                    break

                page_jobs = _parse_visasponsor_cards(html, max_age, seen_urls, country)
                all_jobs.extend(page_jobs)

                # If fewer than 18 cards, this was the last page — stop paginating
                if len(page_jobs) < 18:
                    break

    log.info("[visasponsor] DONE: %d raw jobs", len(all_jobs))
    return all_jobs


# ── Main pipeline ─────────────────────────────────────────────────────

def _setup_logging(debug):
    """Configure logging: INFO to stderr + file, DEBUG to file only when --debug."""
    log_path = BASE_DIR / "scanner.log"
    level = logging.DEBUG if debug else logging.INFO
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")

    file_h = logging.FileHandler(log_path, mode="w")
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(fmt)

    stderr_h = logging.StreamHandler(sys.stderr)
    stderr_h.setLevel(level)
    stderr_h.setFormatter(fmt)

    log.setLevel(logging.DEBUG)
    log.addHandler(file_h)
    log.addHandler(stderr_h)


def main():
    global _debug

    args = sys.argv[1:]
    _debug = "--debug" in args
    skip_rapidapi = "--skip-rapidapi" in args
    relocation_only = "--relocation-only" in args

    _setup_logging(_debug)

    max_age = DEFAULT_MAX_AGE
    if "--max-age" in args:
        idx = args.index("--max-age")
        if idx + 1 < len(args):
            max_age = int(args[idx + 1])

    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])
            output_path.parent.mkdir(parents=True, exist_ok=True)

    indeed_mcp_path = None
    if "--indeed-file" in args:
        idx = args.index("--indeed-file")
        if idx + 1 < len(args):
            indeed_mcp_path = Path(args[idx + 1])

    log.info("[scanner] Starting scan (max_age=%d days)", max_age)

    profile = load_profile()
    keys = get_api_keys(profile)
    target_companies = get_target_companies(profile)
    in_pipeline = get_in_pipeline_companies(profile)

    history = load_history()
    initial_history_size = len(history)

    # ── Scan all sources concurrently ────────────────────────────────

    raw_jobs = []

    # Indeed MCP file is local-only, run synchronously first
    if indeed_mcp_path and indeed_mcp_path.exists():
        try:
            mcp_jobs = json.loads(indeed_mcp_path.read_text())
            count = 0
            for j in mcp_jobs:
                raw_jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company", ""),
                    "location": j.get("location", ""),
                    "url": j.get("url", ""),
                    "source": "indeed_mcp",
                    "snippet": j.get("snippet", "")[:400],
                    "age_days": j.get("age_days"),
                })
                count += 1
            log.info("[indeed_mcp] DONE: %d jobs from MCP file", count)
        except (json.JSONDecodeError, OSError) as e:
            log.error("[indeed_mcp] ERROR reading %s: %s", indeed_mcp_path, e)
    elif indeed_mcp_path:
        log.info("[indeed_mcp] SKIP: file not found: %s", indeed_mcp_path)

    source_fns = {
        "adzuna": lambda: scan_adzuna(keys["adzuna_app_id"], keys["adzuna_app_key"], max_age),
        "remotive": scan_remotive,
        "greenhouse": scan_greenhouse,
        "lever": scan_lever,
        "smartrecruiters": scan_smartrecruiters,
        "landing.jobs": lambda: scan_landing_jobs(max_age),
        "relocate.me": lambda: scan_relocate_me(max_age),
        "visasponsor": lambda: scan_visasponsor(max_age),
    }
    if not skip_rapidapi:
        source_fns["jsearch"] = lambda: scan_jsearch(keys["rapidapi_key"], max_age, profile)
    else:
        log.info("[jsearch] SKIPPED (--skip-rapidapi flag)")

    with ThreadPoolExecutor(max_workers=SOURCE_WORKERS) as pool:
        futures = {pool.submit(fn): name for name, fn in source_fns.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                jobs = future.result()
                raw_jobs.extend(jobs)
                log.info("[scanner] %s returned %d jobs (total raw: %d)", name, len(jobs), len(raw_jobs))
            except Exception as e:
                log.error("[scanner] %s FAILED: %s", name, e)

    log.info("[scanner] Raw results: %d", len(raw_jobs))

    # ── Pre-filter ────────────────────────────────────────────────────

    filtered = []
    stats = {
        "title_excluded": 0,
        "no_include_signal": 0,
        "in_pipeline": 0,
        "too_old": 0,
        "duplicate_history": 0,
        "duplicate_batch": 0,
        "passed": 0,
    }

    batch_keys = set()

    for job in raw_jobs:
        title = job["title"]
        company = job["company"]
        snippet = job.get("snippet", "")
        age = job.get("age_days")

        # 1. Hard-exclude by title
        if not passes_title_filter(title):
            stats["title_excluded"] += 1
            log.debug("[EXCLUDE title] %s | %s", company, title)
            continue

        # 2. Age filter
        if age is not None and age > max_age:
            stats["too_old"] += 1
            continue

        # 3. Include filter (keywords or target company)
        # Relocation-specific boards (landing.jobs, relocate.me) already pre-filter
        # for international candidates, so keyword filter is mandatory (strict) but
        # the role is treated as pre-qualified — skip company-board strictness.
        source = job.get("source", "")
        is_company_board = "/" in source
        is_relocation_board = source in ("landing.jobs", "relocate.me", "visasponsor")
        # For relocation boards, use the same strict=True keyword filter
        # (we don't want completely off-topic roles) but don't need target-company bypass
        if not passes_include_filter(title, snippet, target_companies, company,
                                     strict=is_company_board or is_relocation_board):
            stats["no_include_signal"] += 1
            log.debug("[NO SIGNAL] %s | %s", company, title)
            continue

        # 4. Recently applied check
        if is_in_active_pipeline(company, in_pipeline):
            stats["in_pipeline"] += 1
            log.debug("[IN_PIPELINE] %s | %s", company, title)
            continue

        # 5. Dedup against history
        dk = dedup_key(company, title)
        if dk in history:
            stats["duplicate_history"] += 1
            continue

        # 6. Dedup within batch
        if dk in batch_keys:
            stats["duplicate_batch"] += 1
            continue
        batch_keys.add(dk)

        # Passed all filters
        stats["passed"] += 1
        out = {
            "title": title,
            "company": company,
            "location": job["location"],
            "url": job["url"],
            "source": job["source"],
            "snippet": snippet,
        }
        # Carry through relocation flag if set by source scanner
        if job.get("relocation"):
            out["relocation"] = True
        filtered.append(out)

        # Add to history
        history[dk] = {
            "title": title,
            "company": company,
            "date_first_seen": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source": job["source"],
        }

    # Save updated history
    save_history(history)

    summary = (
        f"\n{'=' * 50}\n"
        f"Scan Summary\n"
        f"{'=' * 50}\n"
        f"Raw results:       {len(raw_jobs)}\n"
        f"Title excluded:    {stats['title_excluded']}\n"
        f"No include signal: {stats['no_include_signal']}\n"
        f"In pipeline (blocked): {stats['in_pipeline']}\n"
        f"Too old:           {stats['too_old']}\n"
        f"Dup (history):     {stats['duplicate_history']}\n"
        f"Dup (batch):       {stats['duplicate_batch']}\n"
        f"Passed filters:    {stats['passed']}\n"
        f"History entries:   {initial_history_size} -> {len(history)}\n"
        f"{'=' * 50}"
    )
    log.info(summary)

    output_json = json.dumps(filtered, indent=2)
    print(output_json)

    if output_path:
        output_path.write_text(output_json)
        log.info("[scanner] Results saved to %s", output_path)


if __name__ == "__main__":
    main()
