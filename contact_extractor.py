"""
contact_extractor.py
────────────────────
Extracts contact info (email, phone, contact-page URL) from a business
website and detects whether a CDN / Varnish cache is already in use.

Both functions are fast (<5 s), use only requests + BeautifulSoup, and
fail gracefully — they never raise, they return empty/unknown values.
"""
from __future__ import annotations
import re
import random
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ─── user-agent pool ──────────────────────────────────────────────────────────
_UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

def _headers():
    return {
        "User-Agent": random.choice(_UA),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }


# ─── CDN / Varnish / Cache detection ─────────────────────────────────────────

# Maps response-header keywords → human-readable CDN name
_CDN_HEADER_MAP = {
    # Via / X-Cache headers (set by Varnish, Squid, Nginx, etc.)
    "varnish":          "Varnish Cache",
    "squid":            "Squid Cache",
    "nginx":            "nginx Cache",
    # Cloudflare
    "cloudflare":       "Cloudflare",
    "cf-ray":           "Cloudflare",
    "cf-cache-status":  "Cloudflare",
    # Fastly
    "fastly":           "Fastly CDN",
    "x-served-by":      "Fastly CDN",      # header name (Fastly uses this)
    "x-cache":          "Cache (generic)",
    # AWS CloudFront
    "cloudfront":       "AWS CloudFront",
    "x-amz-cf":         "AWS CloudFront",
    # Akamai
    "akamai":           "Akamai CDN",
    "x-check-cacheable":"Akamai CDN",
    # BunnyCDN
    "bunny":            "BunnyCDN",
    "b-cdn":            "BunnyCDN",
    # Sucuri
    "sucuri":           "Sucuri WAF/CDN",
    # KeyCDN
    "keycdn":           "KeyCDN",
    # Imperva / Incapsula
    "incapsula":        "Imperva/Incapsula",
    "x-iinfo":          "Imperva/Incapsula",
    # StackPath / MaxCDN
    "stackpath":        "StackPath CDN",
    # Generic cache hits
    "x-cache-hit":      "Cache (generic)",
    "x-proxy-cache":    "Cache (generic)",
}

# Header names that reliably signal a CDN when present at all
_CDN_HEADER_NAMES = {
    "cf-ray", "cf-cache-status",           # Cloudflare
    "x-served-by",                          # Fastly
    "x-amz-cf-id", "x-amz-cf-pop",         # CloudFront
    "x-check-cacheable",                    # Akamai
    "x-iinfo",                              # Imperva
    "x-cache-hit", "x-proxy-cache",        # generic hit headers
    "bunny-cdn-cache-status",               # BunnyCDN
}

def detect_cdn(url: str, timeout: int = 10) -> dict:
    """
    Check response headers to determine whether the site is already behind
    a CDN or caching layer.

    Returns:
        {
            "has_cdn":    bool,
            "cdn_name":   str | None,   # e.g. "Cloudflare", "Varnish Cache"
            "is_hot_lead": bool,         # True if NO cdn detected → fast.site opportunity
            "raw_signals": [str],        # debug: which headers fired
        }
    """
    result = {
        "has_cdn":     False,
        "cdn_name":    None,
        "is_hot_lead": True,
        "raw_signals": [],
    }
    try:
        resp = requests.head(
            url, headers=_headers(), timeout=timeout,
            allow_redirects=True, stream=False,
        )
        headers_lc = {k.lower(): v.lower() for k, v in resp.headers.items()}

        detected_names: list[str] = []

        # 1. Check whether a CDN header NAME is present at all
        for hname in _CDN_HEADER_NAMES:
            if hname in headers_lc:
                result["raw_signals"].append(f"header present: {hname}")
                # map to friendly name
                for kw, name in _CDN_HEADER_MAP.items():
                    if kw in hname:
                        detected_names.append(name)
                        break
                else:
                    detected_names.append("Cache (generic)")

        # 2. Check header VALUES for CDN keywords
        for hname, hval in headers_lc.items():
            full = f"{hname}: {hval}"
            for kw, name in _CDN_HEADER_MAP.items():
                if kw in full and name not in detected_names:
                    detected_names.append(name)
                    result["raw_signals"].append(f"keyword '{kw}' in {hname}")

        if detected_names:
            # De-duplicate; prefer more specific over "Cache (generic)"
            specific = [n for n in detected_names if n != "Cache (generic)"]
            result["cdn_name"]    = specific[0] if specific else detected_names[0]
            result["has_cdn"]     = True
            result["is_hot_lead"] = False

    except Exception as e:
        result["raw_signals"].append(f"error: {e}")

    return result


# ─── Contact info extraction ──────────────────────────────────────────────────

_EMAIL_RE   = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I
)
_PHONE_RE   = re.compile(
    r"(?:\+?\d[\d\s\-().]{6,}\d)", re.I
)
_CONTACT_PAGE_HINTS = [
    "/contact", "/contact-us", "/contactus", "/get-in-touch",
    "/reach-us", "/support", "/about", "/about-us",
    "/impressum", "/kontakt",
]

# Domains we never want to return as emails
_EMAIL_BLACKLIST = {
    "example.com", "domain.com", "yoursite.com", "sentry.io",
    "w3.org", "schema.org", "google.com", "facebook.com",
    "wixpress.com", "squarespace.com", "wordpress.com",
}

def _clean_emails(raw: list[str]) -> list[str]:
    out = []
    for e in raw:
        e = e.strip().lower()
        domain = e.split("@")[-1]
        if domain in _EMAIL_BLACKLIST:
            continue
        # Skip obvious image / CSS filenames that contain "@" by accident
        if any(e.endswith(ext) for ext in (".png", ".jpg", ".gif", ".css", ".js")):
            continue
        if e not in out:
            out.append(e)
    return out[:5]  # max 5 emails


def _scrape_page(url: str, timeout: int = 8) -> tuple[str, dict]:
    """Fetch a URL; return (html_text, response_headers_lc)."""
    try:
        r = requests.get(
            url, headers=_headers(), timeout=timeout,
            allow_redirects=True,
        )
        return r.text, {k.lower(): v for k, v in r.headers.items()}
    except Exception:
        return "", {}


def _extract_from_html(html: str) -> tuple[list[str], list[str], str | None]:
    """Return (emails, phones, contact_page_url_hint) from raw HTML."""
    emails = _EMAIL_RE.findall(html)
    phones = _PHONE_RE.findall(html)

    # Look for a contact-page link
    soup = BeautifulSoup(html, "lxml")
    contact_href = None
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(hint in href for hint in _CONTACT_PAGE_HINTS):
            contact_href = a["href"]
            break

    return emails, phones, contact_href


def extract_contact_info(url: str) -> dict:
    """
    Scrape the homepage and (if found) the /contact page of `url`.

    Returns:
        {
            "emails":        [str],
            "phones":        [str],
            "contact_page":  str | None,   # full URL of contact page if found
            "primary_email": str | None,   # best single email to use
        }
    """
    result: dict = {
        "emails":        [],
        "phones":        [],
        "contact_page":  None,
        "primary_email": None,
    }

    # 1. Scrape homepage
    html, _ = _scrape_page(url)
    if not html:
        return result

    emails, phones, contact_href = _extract_from_html(html)

    # 2. Also try obvious /contact paths even if not linked from homepage
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    contact_candidates = []
    if contact_href:
        full = urljoin(url, contact_href)
        contact_candidates.append(full)
    # always try /contact as well
    for hint in _CONTACT_PAGE_HINTS[:4]:
        contact_candidates.append(base + hint)

    for contact_url in contact_candidates:
        try:
            c_html, _ = _scrape_page(contact_url, timeout=6)
            if c_html:
                c_emails, c_phones, _ = _extract_from_html(c_html)
                emails  += c_emails
                phones  += c_phones
                # If this page loaded (not 404), record it
                if not result["contact_page"] and c_html.strip():
                    result["contact_page"] = contact_url
                break   # stop after first successful contact page
        except Exception:
            continue

    result["emails"] = _clean_emails(emails)
    # Clean phones: dedupe and cap
    seen_phones: list[str] = []
    for p in phones:
        p = p.strip()
        if p and p not in seen_phones and len(p) >= 7:
            seen_phones.append(p)
    result["phones"] = seen_phones[:3]

    if result["emails"]:
        result["primary_email"] = result["emails"][0]

    return result
