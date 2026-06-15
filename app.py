from __future__ import annotations
import io
import re
import time
import json
import socket
import random
import requests
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pypdf import PdfWriter

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="fast.site — Lead Finder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# PROFESSIONAL LIGHT THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp { background: #F7F8FA !important; }
#root > div:first-child { margin-top: 0 !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container {
    padding: 2rem 3rem 3rem 3rem !important;
    padding-top: 2rem !important;
    margin-top: 0 !important;
    max-width: 1200px !important;
}
h1 {
    font-size: 1.9rem !important; font-weight: 700 !important;
    color: #0F1623 !important; letter-spacing: -0.5px !important;
    margin-bottom: 0.25rem !important;
}
h2, h3 { font-weight: 600 !important; color: #1A2233 !important; letter-spacing: -0.3px !important; }
p, li, label, .stMarkdown { color: #2D3748 !important; font-size: 0.95rem !important; line-height: 1.6 !important; }
small, .stCaption, [data-testid="stCaptionContainer"] { color: #6B7A99 !important; font-size: 0.82rem !important; }
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #FFFFFF !important; border: 1.5px solid #D8DEE9 !important;
    border-radius: 8px !important; color: #1A2233 !important;
    font-size: 0.94rem !important; padding: 0.55rem 0.85rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2563EB !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}
.stTextInput label, .stNumberInput label, .stRadio label {
    font-weight: 500 !important; font-size: 0.87rem !important;
    color: #374151 !important; margin-bottom: 4px !important;
}
.stButton > button[kind="primary"], button[data-testid="baseButton-primary"] {
    background: #2563EB !important; color: #FFFFFF !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.9rem !important;
    padding: 0.55rem 1.2rem !important; letter-spacing: 0.01em !important;
    transition: background 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.18) !important;
}
.stButton > button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
    background: #1D4ED8 !important; box-shadow: 0 4px 12px rgba(37,99,235,0.28) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #FFFFFF !important; color: #374151 !important;
    border: 1.5px solid #D1D9E8 !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 0.9rem !important;
    transition: border-color 0.18s ease, background 0.18s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #2563EB !important; color: #2563EB !important; background: #EFF6FF !important;
}
[data-testid="stDownloadButton"] > button {
    background: #2563EB !important; color: #FFFFFF !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.9rem !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.18) !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #1D4ED8 !important; }
.stRadio > div { gap: 1rem !important; flex-direction: row !important; }
.stRadio > div > label {
    background: #FFFFFF !important; border: 1.5px solid #D8DEE9 !important;
    border-radius: 8px !important; padding: 0.5rem 1rem !important;
    cursor: pointer !important; transition: border-color 0.18s, background 0.18s !important;
    font-weight: 500 !important; color: #374151 !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: #2563EB !important; background: #EFF6FF !important; color: #1D4ED8 !important;
}
[data-testid="stAlert"] { border-radius: 8px !important; border-left-width: 4px !important; font-size: 0.91rem !important; }
[data-testid="stMetric"] {
    background: #FFFFFF !important; border: 1px solid #E5EAF3 !important;
    border-radius: 10px !important; padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.82rem !important; font-weight: 600 !important;
    color: #6B7A99 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; color: #0F1623 !important; }
[data-testid="stExpander"] {
    background: #FFFFFF !important; border: 1px solid #E5EAF3 !important;
    border-radius: 10px !important; margin-bottom: 0.75rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important; overflow: hidden !important;
}
[data-testid="stExpander"] summary { font-weight: 600 !important; font-size: 0.95rem !important; color: #1A2233 !important; padding: 0.85rem 1.1rem !important; }
[data-testid="stExpander"] summary:hover { background: #F7F8FA !important; }
hr { border: none !important; border-top: 1px solid #E5EAF3 !important; margin: 1rem 0 !important; }
.stCheckbox label { color: #374151 !important; font-weight: 400 !important; }
.stProgress > div > div { background: #2563EB !important; border-radius: 99px !important; }
.stProgress > div { border-radius: 99px !important; background: #E5EAF3 !important; }
[data-testid="stSpinner"] p { color: #6B7A99 !important; font-size: 0.9rem !important; }
.tech-badge {
    display: inline-block; padding: 3px 10px; border-radius: 99px;
    font-size: 11px; font-weight: 600; margin: 2px 2px; letter-spacing: 0.02em;
}
.score-chip {
    display: inline-block; padding: 4px 14px; border-radius: 99px;
    font-size: 13px; font-weight: 700; margin: 0 4px;
}
.app-header {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 1.75rem; padding-bottom: 1.25rem; border-bottom: 1px solid #E5EAF3;
}
.app-header-icon {
    width: 44px; height: 44px; background: #2563EB; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.app-header-title { font-size: 1.45rem !important; font-weight: 700 !important; color: #0F1623 !important; line-height: 1.2 !important; margin: 0 !important; }
.app-header-sub { font-size: 0.85rem; color: #6B7A99; margin: 0; }
.step-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #EFF6FF; color: #2563EB; border-radius: 99px;
    padding: 4px 12px; font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem;
}
.result-card {
    background: #FFFFFF; border: 1px solid #E5EAF3; border-radius: 10px;
    padding: 1rem 1.25rem; margin-bottom: 0.6rem; transition: box-shadow 0.18s;
}
.result-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.07); border-color: #CBD5E8; }
.app-footer {
    margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #E5EAF3;
    font-size: 0.8rem; color: #9AA5BC; text-align: center;
}
.lang-selector {
    display: flex; align-items: center; justify-content: center;
    min-height: 60vh; flex-direction: column; gap: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE SELECTION — shown once at startup, stored in session_state
# ─────────────────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.markdown("""
<div style="display:flex;align-items:center;justify-content:center;min-height:55vh;flex-direction:column;gap:1.5rem;">
  <div style="text-align:center;">
    <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔎</div>
    <div style="font-size:2rem;font-weight:700;color:#0F1623;margin-bottom:0.4rem;">fast.site <span style="color:#2563EB;font-weight:400;font-size:1.3rem;">Lead Finder</span></div>
    <div style="font-size:1rem;color:#6B7A99;">Choose your language &nbsp;·&nbsp; Sprache wählen</div>
  </div>
</div>
""", unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([2, 2, 2])
    with col_mid:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        if st.button("🇬🇧  English", use_container_width=True, type="primary"):
            st.session_state["lang"] = "en"
            st.rerun()
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("🇩🇪  Deutsch", use_container_width=True):
            st.session_state["lang"] = "de"
            st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATION HELPER
# ─────────────────────────────────────────────────────────────────────────────
_LANG: str = st.session_state.get("lang", "en")

def _t(en: str, de: str) -> str:
    return de if _LANG == "de" else en

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH — delegate entirely to search.py (no duplication)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from search import search as _search_engine
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

def multi_engine_search(industry: str, area: str, max_results: int = 20) -> tuple[list[dict], list[str]]:
    """Delegate to search.py's search() function."""
    if not SEARCH_AVAILABLE:
        return [], [_t("search.py not found", "search.py nicht gefunden")]
    results, engine = _search_engine(industry, area, max_results)
    return results, [engine] if isinstance(engine, str) else engine

# ─────────────────────────────────────────────────────────────────────────────
# TECH DETECTION  — CMS signatures & plugin detection
# ─────────────────────────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/123.0.0.0",
]

def _headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

CMS_SIGNATURES: dict[str, list[tuple[str, float]]] = {
    "WordPress": [
        (r"/wp-content/themes/", 2.0), (r"/wp-content/plugins/", 2.0),
        (r"/wp-includes/js/", 2.0), (r"/wp-json/", 1.5),
        (r"wp-embed\.min\.js", 1.5), (r'content="WordPress', 1.5),
        (r"xmlrpc\.php", 1.0), (r"/wp-content/uploads/", 1.0),
        (r"wp-block-", 0.8), (r"class=\"wp-", 0.7), (r"WordPress", 0.5),
    ],
    "Shopify": [
        (r"cdn\.shopify\.com", 2.0), (r"myshopify\.com", 2.0),
        (r"Shopify\.theme", 2.0), (r"shopify-section", 1.5),
        (r"shopify\.com/s/files/", 1.5), (r'"shopify"', 1.0),
        (r"Shopify\.shop", 1.0), (r"/collections/", 0.5),
    ],
    "Wix": [
        (r"wixstatic\.com", 2.0), (r"wix\.com/_api/", 2.0),
        (r"X-Wix-Published-Version", 2.0), (r"wix-code", 1.5),
        (r"\"wix\"", 1.0), (r"parastorage\.com", 1.0), (r"wixsite\.com", 1.5),
    ],
    "Squarespace": [
        (r"squarespace\.com", 2.0), (r"sqsp\.net", 2.0),
        (r"static1\.squarespace\.com", 2.0), (r'"squarespace"', 1.5),
        (r"Squarespace-Headers", 1.5), (r"sqs-layout", 1.0), (r"data-sqs-type", 1.0),
    ],
    "Webflow": [
        (r"webflow\.com", 2.0), (r"webflow\.io", 2.0),
        (r"data-wf-page", 2.0), (r"data-wf-site", 2.0),
        (r"webflow\.js", 1.5), (r'"webflow"', 1.0),
    ],
    "Joomla": [
        (r"/components/com_content", 2.0), (r"/components/com_", 1.5),
        (r'content="Joomla', 2.0), (r"joomla", 1.0),
        (r"/media/system/js/", 0.8), (r"Joomla!", 0.8), (r"/administrator/", 0.5),
    ],
    "Drupal": [
        (r"/sites/default/files/", 2.0), (r"Drupal\.settings", 2.0),
        (r'content="Drupal', 2.0), (r"drupal\.js", 1.5),
        (r"drupal", 0.8), (r"/misc/drupal\.js", 1.5), (r"X-Generator.*Drupal", 2.0),
    ],
    "Magento": [
        (r"Mage\.Cookies", 2.0), (r"/skin/frontend/", 2.0),
        (r"magento", 1.0), (r"var BLANK_URL", 1.0),
        (r"Magento_", 1.5), (r"/pub/static/frontend/", 1.5),
    ],
    "Ghost": [
        (r"content\.ghost\.io", 2.0), (r"ghost\.io", 1.5),
        (r'content="Ghost', 2.0), (r"ghost-theme", 1.5), (r"/ghost/api/", 2.0),
    ],
    "Next.js": [(r"_next/static/chunks/", 2.0), (r"__NEXT_DATA__", 2.0), (r"_next/image", 1.5)],
    "Nuxt.js": [(r"__nuxt", 2.0), (r"_nuxt/", 2.0), (r"nuxt-link", 1.5), (r"window\.__nuxt", 2.0)],
    "Gatsby":  [(r"gatsby-", 1.5), (r"/static/gatsby-", 2.0), (r"window\.___gatsby", 2.0)],
    "HubSpot CMS": [(r"hs-scripts\.com", 2.0), (r"hubspot\.com", 1.5), (r"hs-analytics", 1.5)],
    "Framer": [(r"framer\.com", 2.0), (r"framerusercontent\.com", 2.0)],
    "BigCommerce": [(r"bigcommerce\.com", 2.0), (r"cdn\.bigcommerce\.com", 2.0)],
}

HEADER_CMS_MAP: dict[str, str] = {
    "x-shopify-stage": "Shopify", "x-shopid": "Shopify",
    "x-wix-request-id": "Wix", "x-ghost-cache-status": "Ghost",
    "x-drupal-cache": "Drupal", "x-generator": None,
    "x-powered-by-squarespace": "Squarespace",
}

GENERATOR_MAP: dict[str, str] = {
    "wordpress": "WordPress", "joomla": "Joomla", "drupal": "Drupal",
    "ghost": "Ghost", "craft cms": "Craft CMS", "typo3": "TYPO3",
    "squarespace": "Squarespace", "webflow": "Webflow", "framer": "Framer",
    "wix": "Wix", "blogger": "Blogger", "hubspot": "HubSpot CMS",
    "bigcommerce": "BigCommerce", "prestashop": "PrestaShop",
    "opencart": "OpenCart", "magento": "Magento",
}

_INFRASTRUCTURE_LABELS: dict[str, str] = {
    "cloudflare": "Cloudflare CDN", "fastly": "Fastly CDN",
    "akamai": "Akamai CDN", "cloudfront": "AWS CloudFront",
    "bunnycdn": "BunnyCDN", "b-cdn": "BunnyCDN",
}

PLUGIN_SIGNATURES: dict[str, str] = {
    "WooCommerce": r"woocommerce", "Elementor": r"elementor",
    "Yoast SEO": r"yoast|yoast-schema", "Rank Math SEO": r"rank-math|rankmath",
    "Contact Form 7": r"wpcf7|contact-form-7", "Gravity Forms": r"gform_|gravityforms",
    "WPML": r"\bwpml\b", "Akismet": r"akismet", "Jetpack": r"jetpack",
    "WP Rocket": r"wp-rocket|wprocket", "All-in-One SEO": r"aioseo|all-in-one-seo",
    "Divi Builder": r"divi|et_pb_", "WPBakery": r"wpb_|vc_",
    "Beaver Builder": r"fl-builder|beaver-builder",
    "Google Analytics 4": r"G-[A-Z0-9]{6,}|gtag\(.*G-",
    "Google Analytics UA": r"UA-\d{5,}-\d+",
    "Google Tag Manager": r"googletagmanager\.com|GTM-[A-Z0-9]+",
    "Facebook Pixel": r"fbq\(|facebook\.net/en_US/fbevents",
    "Hotjar": r"hotjar\.com|hjid", "Clarity (Microsoft)": r"clarity\.ms|microsoft.*clarity",
    "Mixpanel": r"mixpanel\.com", "Segment": r"segment\.com|analytics\.js",
    "Intercom": r"intercom\.io|intercomcdn", "Tawk.to": r"tawk\.to",
    "Zendesk Chat": r"zendesk\.com|zopim\.com", "Crisp Chat": r"crisp\.chat",
    "Drift": r"drift\.com", "Tidio": r"tidio", "LiveChat": r"livechatinc\.com",
    "Cloudflare": r"cloudflare", "Fastly": r"fastly",
    "AWS CloudFront": r"cloudfront\.net", "Akamai": r"akamai",
    "reCAPTCHA": r"recaptcha", "hCaptcha": r"hcaptcha",
    "Bootstrap": r"bootstrap\.min\.css|bootstrap\.css|bootstrap\.min\.js",
    "Tailwind CSS": r"tailwind|tailwindcss", "jQuery": r"jquery\.min\.js|jquery-\d",
    "React": r"react\.production\.min|react-dom|__react",
    "Vue.js": r"vue\.global|vue\.esm|vue@\d|createApp\(",
    "Angular": r"angular\.min\.js|ng-version|zone\.js",
    "Alpine.js": r"alpine\.min\.js|x-data=",
    "Next.js": r"__NEXT_DATA__|_next/static",
    "Nuxt.js": r"__nuxt|_nuxt/", "Svelte": r"svelte-",
    "Stripe": r"stripe\.com/v3|js\.stripe\.com", "PayPal": r"paypal\.com/sdk",
    "HubSpot Forms": r"hsforms\.net|hbspt\.forms", "Mailchimp": r"mailchimp\.com|mc\.js",
    "Klaviyo": r"klaviyo\.com|kl-private", "ActiveCampaign": r"activecampaign\.com",
    "Cookiebot": r"cookiebot\.com", "OneTrust": r"onetrust\.com|onetrust-banner",
    "CookieYes": r"cookieyes\.com",
}

def _extract_generator_meta(soup) -> str | None:
    tag = soup.find("meta", attrs={"name": re.compile(r"^generator$", re.I)})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None

def _resolve_unknown_cms(t: dict) -> tuple[str, str | None]:
    plugins_lc = " ".join(t.get("plugins", [])).lower()
    svr_raw    = t.get("server") or ""
    svr_lc     = svr_raw.lower()
    if "next.js" in plugins_lc:   return "Next.js", "medium"
    if "nuxt.js" in plugins_lc:   return "Nuxt.js", "medium"
    if "react"   in plugins_lc:   return "Custom (React)", "low"
    if "angular" in plugins_lc:   return "Custom (Angular)", "low"
    if "vue.js"  in plugins_lc:   return "Custom (Vue)", "low"
    if "wordpress" in plugins_lc or "woocommerce" in plugins_lc: return "WordPress", "medium"
    if "shopify"    in plugins_lc: return "Shopify", "medium"
    if "wix"        in plugins_lc: return "Wix", "medium"
    if "squarespace"in plugins_lc: return "Squarespace", "medium"
    if "webflow"    in plugins_lc: return "Webflow", "medium"
    if "drupal"     in plugins_lc: return "Drupal", "medium"
    if "joomla"     in plugins_lc: return "Joomla", "medium"
    if "svelte"     in plugins_lc: return "Custom (Svelte)", "low"
    if "gatsby"     in plugins_lc: return "Gatsby", "low"
    if svr_lc:
        for infra_key, infra_label in _INFRASTRUCTURE_LABELS.items():
            if infra_key in svr_lc:
                return f"Hidden behind {infra_label}", "low"
        if "php" in svr_lc:
            return "Custom PHP site", "low"
        svr_label = svr_raw.split("/")[0].strip()[:20] or "Unknown server"
        return f"Custom site ({svr_label})", "low"
    return "Unknown", None

def detect_tech(url: str, timeout: int = 12) -> dict:
    result: dict = {
        "cms": "Unknown", "cms_confidence": None,
        "plugins": [], "frameworks": [],
        "server": None, "https": url.startswith("https"), "ip": None, "error": None,
    }
    try:
        resp     = requests.get(url, headers=_headers(), timeout=timeout, allow_redirects=True, stream=False)
        raw_html = resp.text
        html_lc  = raw_html.lower()
        hdrs     = resp.headers
        hdrs_lc  = {k.lower(): v.lower() for k, v in hdrs.items()}
        soup     = BeautifulSoup(raw_html, "lxml")

        result["server"] = (hdrs.get("Server") or hdrs.get("X-Powered-By") or hdrs.get("x-powered-by") or None)
        try:
            result["ip"] = socket.gethostbyname(urlparse(url).netloc)
        except Exception:
            pass

        cms_detected = "Unknown"
        confidence   = None

        gen = _extract_generator_meta(soup)
        if gen:
            gen_lc = gen.lower()
            for keyword, cms_name in GENERATOR_MAP.items():
                if keyword in gen_lc:
                    cms_detected = cms_name; confidence = "high"; break

        if cms_detected == "Unknown":
            for hdr_key, cms_name in HEADER_CMS_MAP.items():
                if hdr_key in hdrs_lc:
                    if cms_name:
                        cms_detected = cms_name; confidence = "high"; break
                    elif hdr_key == "x-generator":
                        val = hdrs_lc[hdr_key]
                        for keyword, cname in GENERATOR_MAP.items():
                            if keyword in val:
                                cms_detected = cname; confidence = "high"; break
                    if cms_detected != "Unknown":
                        break
            if cms_detected == "Unknown":
                xpb = hdrs_lc.get("x-powered-by", "")
                for keyword, cname in GENERATOR_MAP.items():
                    if keyword in xpb:
                        cms_detected = cname; confidence = "high"; break

        if cms_detected == "Unknown":
            best_cms = "Unknown"; best_score = 0.0
            combined = html_lc + " " + str(hdrs_lc)
            for cms_name, patterns in CMS_SIGNATURES.items():
                total = sum(w for pat, w in patterns if re.search(pat, combined, re.I))
                if total > best_score:
                    best_score = total; best_cms = cms_name
            if best_score >= 2.0:
                cms_detected = best_cms
                confidence   = "high" if best_score >= 3.0 else "medium"
            elif best_score >= 1.0:
                cms_detected = best_cms; confidence = "low"

        result["cms"]            = cms_detected
        result["cms_confidence"] = confidence
        found = [name for name, pat in PLUGIN_SIGNATURES.items() if re.search(pat, html_lc, re.I)]
        result["plugins"] = found
    except Exception as e:
        result["error"] = str(e)
    return result

# ─────────────────────────────────────────────────────────────────────────────
# AUDIT
# ─────────────────────────────────────────────────────────────────────────────
try:
    from audit import audit_website
    from audit_pdf import generate_audit_pdf
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False
    def audit_website(url, progress_callback=None):
        try:
            start = time.time()
            r     = requests.get(url, headers=_headers(), timeout=15)
            ttfb  = round((time.time() - start) * 1000)
            soup  = BeautifulSoup(r.text, "lxml")
        except Exception:
            return {"url": url, "overall_score": 0, "breakdown": {}, "lighthouse_details": {}, "fastsite_projection": {}}
        score = 0; issues = []; strengths = []
        if url.startswith("https"):
            score += 15; strengths.append("HTTPS enabled")
        else:
            issues.append("No HTTPS")
        title = soup.find("title")
        if title and title.get_text(strip=True):
            score += 10; strengths.append("Title tag present")
        else:
            issues.append("Missing title tag")
        h1s = soup.find_all("h1")
        if len(h1s) == 1:   score += 10; strengths.append("Single H1 tag")
        elif not h1s:        issues.append("No H1 tag")
        meta = soup.find("meta", attrs={"name": re.compile("description", re.I)})
        if meta and meta.get("content", "").strip():
            score += 10; strengths.append("Meta description present")
        else:
            issues.append("No meta description")
        ttfb_score = 30 if ttfb < 500 else (20 if ttfb < 1000 else 5)
        score += ttfb_score
        if ttfb < 500: strengths.append(f"Fast TTFB: {ttfb}ms")
        else:          issues.append(f"Slow TTFB: {ttfb}ms")
        return {
            "url": url, "overall_score": min(score + 25, 100),
            "breakdown": {"seo": {"score": score, "issues": issues, "strengths": strengths, "details": {}}},
            "lighthouse_details": {}, "fastsite_projection": {},
        }

    def generate_audit_pdf(audit, lang="en"):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            buf    = io.BytesIO()
            doc    = SimpleDocTemplate(buf, pagesize=A4)
            styles = getSampleStyleSheet()
            story  = [Paragraph(f"Audit: {audit.get('url')}", styles["Title"]),
                      Paragraph(f"Score: {audit.get('overall_score')}/100", styles["Normal"])]
            for cat, data in audit.get("breakdown", {}).items():
                story.append(Paragraph(f"{cat}: {data.get('score')}/100", styles["Heading2"]))
                for iss in data.get("issues", []):
                    story.append(Paragraph(f"[!] {iss}", styles["Normal"]))
            doc.build(story)
            return buf.getvalue()
        except Exception:
            return b"%PDF-placeholder"

# ─── Lead generation tools ────────────────────────────────────────────────────
try:
    from lead_tools import (
        varnish_opportunity_score,
        opportunity_label,
        generate_cold_email,
        build_leads_csv,
    )
    LEAD_TOOLS_AVAILABLE = True
except ImportError:
    LEAD_TOOLS_AVAILABLE = False
    def varnish_opportunity_score(audit): return 0
    def opportunity_label(score): return ("—", "#888")
    def generate_cold_email(**kw): return "lead_tools.py not found"
    def build_leads_csv(*a, **kw): return b""

try:
    from contact_extractor import extract_contact_info, detect_cdn
    CONTACT_AVAILABLE = True
except ImportError:
    CONTACT_AVAILABLE = False
    def extract_contact_info(url): return {"emails": [], "phones": [], "contact_page": None, "primary_email": None}
    def detect_cdn(url): return {"has_cdn": False, "cdn_name": None, "is_hot_lead": True}

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_CMS_COLORS: dict[str, tuple[str, str]] = {
    "WordPress": ("#21759B", "#21759B18"), "Shopify": ("#5E8E3E", "#96BF4818"),
    "Wix": ("#B07D00", "#FAAD1418"), "Squarespace": ("#333333", "#33333318"),
    "Webflow": ("#2D3AC0", "#4353FF18"), "Joomla": ("#C03D1E", "#F44E2718"),
    "Drupal": ("#0678BE", "#0678BE18"), "Magento": ("#C24E12", "#EE672218"),
    "Ghost": ("#738A94", "#738A9418"), "PrestaShop": ("#DF0067", "#DF006718"),
    "Next.js": ("#000000", "#00000015"), "Nuxt.js": ("#00C58E", "#00C58E18"),
    "Gatsby": ("#663399", "#66339918"), "HubSpot CMS": ("#FF7A59", "#FF7A5918"),
    "Framer": ("#0099FF", "#0099FF18"), "BigCommerce": ("#34313F", "#34313F18"),
    "Unknown": ("#888888", "#88888815"),
}

def _cms_badge(cms: str, confidence: str | None = None) -> str:
    fg, bg = _CMS_COLORS.get(cms, ("#888888", "#88888815"))
    conf_icon = {"high": " ✓", "medium": " ~", "low": " "}.get(confidence or "", "")
    return (
        f'<span class="tech-badge" style="background:{bg};color:{fg};'
        f'border:1px solid {fg}55;font-weight:700;">{cms}{conf_icon}</span>'
    )

def _score_color(s):
    return "#2E7D32" if s >= 75 else ("#F57F17" if s >= 50 else "#C62828")

def _render_tech_badges(t: dict) -> str:
    cms  = t.get("cms", "Unknown")
    conf = t.get("cms_confidence")
    if cms == "Unknown":
        cms, conf = _resolve_unknown_cms(t)
    cms_html  = _cms_badge(cms, conf)
    plug_html = " ".join(
        f'<span class="tech-badge" style="background:#6C63FF18;color:#4B44CC;border:1px solid #6C63FF44;">{p}</span>'
        for p in t.get("plugins", [])[:8]
    )
    svr_txt = t.get("server", "")
    svr = (
        f'<span class="tech-badge" style="background:#88888815;color:#555;border:1px solid #88888844;">🖥 {svr_txt[:30]}</span>'
        if svr_txt else ""
    )
    err_txt = t.get("error", "")
    err = (
        f'<span class="tech-badge" style="background:#ff000015;color:#c00;border:1px solid #ff000044;">⚠ {err_txt[:40]}</span>'
        if err_txt else ""
    )
    return cms_html + " " + plug_html + " " + svr + " " + err

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

# ── Language switcher in top-right corner ─────────────────────────────────────
header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown(f"""
<div class="app-header">
  <div class="app-header-icon">⚡</div>
  <div>
    <div class="app-header-title">fast.site &nbsp;<span style="color:#2563EB;font-weight:400;font-size:1rem;">Lead Finder</span></div>
    <div class="app-header-sub">{_t(
        "Find slow websites · Extract contacts · Generate cold emails · Export CSV leads",
        "Langsame Websites finden · Kontakte extrahieren · Kalt-E-Mails generieren · CSV exportieren"
    )}</div>
  </div>
</div>
""", unsafe_allow_html=True)
with header_right:
    st.markdown("<div style='padding-top:0.6rem;'></div>", unsafe_allow_html=True)
    other_lang_label = "🇩🇪 Deutsch" if _LANG == "en" else "🇬🇧 English"
    if st.button(other_lang_label, key="lang_switch"):
        st.session_state["lang"] = "de" if _LANG == "en" else "en"
        # Reset audit state so nothing is stale after language switch
        for k in ["audits", "results", "engines", "tech", "direct_tech",
                  "direct_url_ready", "selected_for_audit", "_select_action"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STEP 1: Mode Selection ─────────────────────────────────────────────────
st.markdown(
    f'<div class="step-pill">{_t("Step 1", "Schritt 1")} &nbsp;·&nbsp; {_t("What do you want to do?", "Was möchten Sie tun?")}</div>',
    unsafe_allow_html=True,
)
st.markdown(f"#### {_t('Pick an option to get started', 'Wählen Sie eine Option, um loszulegen')}")

mode = st.radio(
    _t("Pick an option", "Option wählen"),
    [
        _t("🔍 Find & Check Businesses — Search by type and city",
           "🔍 Unternehmen finden & prüfen — Nach Typ und Stadt suchen"),
        _t("🌐 Check a Website — Paste any website address",
           "🌐 Website prüfen — Beliebige Webadresse eingeben"),
    ],
    horizontal=True,
    label_visibility="collapsed",
)
is_direct_mode = "🌐" in mode

# Clear results on mode switch
prev_mode = st.session_state.get("_active_mode")
if prev_mode is not None and prev_mode != is_direct_mode:
    for key in ["audits", "results", "engines", "tech", "direct_tech",
                "direct_url_ready", "selected_for_audit", "_select_action"]:
        st.session_state.pop(key, None)
st.session_state["_active_mode"] = is_direct_mode

st.markdown("")

# ── MODE A: Direct URL Audit ─────────────────────────────────────────────────
if is_direct_mode:
    st.markdown(f"**{_t('Paste the website address you want to check', 'Fügen Sie die Webadresse ein, die Sie prüfen möchten')}**")
    url_col, btn_col = st.columns([4, 1])
    with url_col:
        direct_url = st.text_input(
            _t("Website address", "Webadresse"),
            placeholder="https://beispiel.de",
            label_visibility="collapsed",
        )
    with btn_col:
        direct_go_btn = st.button(
            f"▶ {_t('Go', 'Los')}",
            type="primary",
            use_container_width=True,
        )

    if direct_go_btn:
        raw = direct_url.strip()
        if not raw:
            st.warning(_t("Please paste a website address first.", "Bitte geben Sie zuerst eine Webadresse ein."))
        else:
            if not raw.startswith(("http://", "https://")):
                raw = "https://" + raw
            st.session_state["direct_url_ready"] = raw
            st.session_state.pop("direct_tech", None)
            st.session_state.pop("audits", None)
            st.session_state.pop("results", None)
            st.rerun()

    ready_url = st.session_state.get("direct_url_ready", "")
    if ready_url:
        st.markdown("")
        st.markdown(
            f'<div class="step-pill">{_t("Step 2", "Schritt 2")} &nbsp;·&nbsp; {_t("See what the site is built with", "Womit die Website gebaut wurde")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"#### {_t('What is this website built with?', 'Womit ist diese Website gebaut?')}")
        st.caption(f"🌐 [{ready_url}]({ready_url})")

        direct_tech      = st.session_state.get("direct_tech", {})
        already_detected = ready_url in direct_tech

        detect_col, skip_col = st.columns([2, 1])
        with detect_col:
            detect_btn = st.button(
                f"🧪 {_t('Find out what tools & platform it uses', 'Herausfinden, welche Tools & Plattform genutzt werden')}",
                use_container_width=True,
                disabled=already_detected,
            )
        with skip_col:
            skip_btn = st.button(
                f"⏭ {_t('Skip this — go straight to the check', 'Überspringen — direkt zur Prüfung')}",
                use_container_width=True,
            )

        if detect_btn:
            with st.spinner(f"{_t('Looking up', 'Nachschlagen')} {ready_url}…"):
                direct_tech[ready_url] = detect_tech(ready_url)
            st.session_state["direct_tech"] = direct_tech
            st.rerun()

        if already_detected:
            t = direct_tech[ready_url]
            st.markdown(
                f"**{_t('Built with', 'Gebaut mit')}:** " + _render_tech_badges(t),
                unsafe_allow_html=True,
            )
            st.success(_t("Done! You can now run the full website check below.",
                          "Fertig! Sie können jetzt die vollständige Website-Prüfung starten."))

        if already_detected or skip_btn:
            st.markdown("")
            st.markdown(
                f'<div class="step-pill">{_t("Step 3", "Schritt 3")} &nbsp;·&nbsp; {_t("Run the check", "Prüfung starten")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"#### {_t('Check this website', 'Diese Website prüfen')}")
            already_has_audit = ready_url in st.session_state.get("audits", {})
            audit_btn_label   = (
                f"🔄 {_t('Check again', 'Erneut prüfen')}" if already_has_audit
                else f"🚀 {_t('Check this website now', 'Jetzt prüfen')}"
            )
            audit_btn = st.button(audit_btn_label, type="primary", use_container_width=True)
            if audit_btn:
                st.session_state.setdefault("audits", {}).pop(ready_url, None)
                with st.spinner(f"{_t('Checking', 'Prüfe')} {ready_url}…"):
                    result = audit_website(ready_url)
                    # Run CDN detection in direct mode too so the banner is accurate
                    if CONTACT_AVAILABLE:
                        cdn_map = st.session_state.get("cdn_map", {})
                        cdn_map[ready_url] = detect_cdn(ready_url)
                        st.session_state["cdn_map"] = cdn_map
                st.session_state["audits"] = {ready_url: result}
                st.rerun()

# ── MODE B: Search Businesses ─────────────────────────────────────────────────
else:
    st.markdown(f"**{_t('Tell us what kind of business and where', 'Sagen Sie uns, welche Art von Unternehmen und wo')}**")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        industry = st.text_input(
            _t("Type of business", "Art des Unternehmens"),
            placeholder=_t("e.g. restaurants, dentists, gyms", "z.B. Restaurants, Zahnärzte, Fitnessstudios"),
        )
    with col2:
        area = st.text_input(
            _t("City or country", "Stadt oder Land"),
            placeholder=_t("e.g. Berlin, Germany, Dubai", "z.B. Berlin, Deutschland, Dubai"),
        )
    with col3:
        max_results = st.number_input(_t("How many?", "Wie viele?"), 1, 50, 15)

    search_btn = st.button(
        f"🔍 {_t('Find Businesses', 'Unternehmen finden')}",
        type="primary",
        use_container_width=True,
    )

    if search_btn:
        if not industry or not area:
            st.warning(_t("Please fill in both fields — type of business and city/country.",
                          "Bitte füllen Sie beide Felder aus — Unternehmensart und Stadt/Land."))
        else:
            status = st.empty()
            with st.spinner(_t("Searching the web for matching businesses…",
                               "Suche im Web nach passenden Unternehmen…")):
                results, engines = multi_engine_search(industry, area, int(max_results))
            st.session_state["results"]            = results
            st.session_state["engines"]            = engines
            st.session_state["tech"]               = {}
            st.session_state["audits"]             = {}
            st.session_state["selected_for_audit"] = []
            st.session_state.pop("direct_url_ready", None)
            status.empty()

# ── STEP 2 (Search mode): Show Results + Tech Detection ──────────────────────
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    engines = st.session_state["engines"]

    st.markdown(
        f'<div class="step-pill">{_t("Step 2", "Schritt 2")} &nbsp;·&nbsp; {_t("Businesses Found", "Gefundene Unternehmen")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"#### {_t('Here are the businesses we found', 'Hier sind die gefundenen Unternehmen')}")
    st.caption(f"{_t('Searched via', 'Gesucht über')}: {' · '.join(engines)}")
    st.info(_t(
        f"Found **{len(results)}** business websites. Tick the ones you want to check, then click the button at the bottom.",
        f"**{len(results)}** Unternehmenswebsites gefunden. Wählen Sie die gewünschten aus und klicken Sie unten auf die Schaltfläche.",
    ))

    if st.button(
        f"🧪 {_t('See what platform each site uses', 'Plattform jeder Website ermitteln')}",
        use_container_width=True,
    ):
        prog   = st.progress(0)
        status = st.empty()
        tech   = {}
        cdn_map = {}
        for i, item in enumerate(results):
            url = item.get("source_url", "")
            status.text(f"{_t('Looking up', 'Untersuche')} {url}…")
            if url:
                tech[url]    = detect_tech(url)
                cdn_map[url] = detect_cdn(url)
            prog.progress((i + 1) / len(results))
        st.session_state["tech"]    = tech
        st.session_state["cdn_map"] = cdn_map
        status.empty(); prog.empty()
        st.success(_t("Done! Platform info is now shown next to each site.",
                      "Fertig! Die Plattforminfo wird jetzt neben jeder Website angezeigt."))

    tech    = st.session_state.get("tech", {})
    cdn_map = st.session_state.get("cdn_map", {})

    if "selected_for_audit" not in st.session_state:
        st.session_state["selected_for_audit"] = []

    all_urls = [item.get("source_url", "") for item in results if item.get("source_url")]
    if "_select_action" not in st.session_state:
        st.session_state["_select_action"] = None

    sel_col1, sel_col2, _ = st.columns([1, 1, 4])
    with sel_col1:
        if st.button(f"☑ {_t('Select All', 'Alle auswählen')}", use_container_width=True):
            st.session_state["selected_for_audit"] = list(all_urls)
            st.session_state["_select_action"] = "all"
            st.rerun()
    with sel_col2:
        if st.button(f"☐ {_t('Clear Selection', 'Auswahl aufheben')}", use_container_width=True):
            st.session_state["selected_for_audit"] = []
            st.session_state["_select_action"] = "none"
            st.rerun()

    selected = st.session_state["selected_for_audit"]

    for idx, item in enumerate(results):
        url  = item.get("source_url", "")
        name = item.get("business_name", url)
        snip = item.get("snippet", "")
        src  = item.get("source", "")
        t    = tech.get(url, {})
        cdn  = cdn_map.get(url, {})
        already_audited = url in st.session_state.get("audits", {})

        with st.container():
            chk_col, info_col, btn_col = st.columns([0.5, 5, 1.5])
            with chk_col:
                action_suffix = st.session_state.get("_select_action", "")
                checked = st.checkbox(
                    f"Select {name}", value=(url in selected),
                    key=f"chk_{idx}_{action_suffix}", label_visibility="collapsed",
                )
                if checked and url not in selected:
                    selected.append(url)
                    st.session_state["selected_for_audit"] = selected
                    st.session_state["_select_action"] = None
                elif not checked and url in selected:
                    selected.remove(url)
                    st.session_state["selected_for_audit"] = selected
                    st.session_state["_select_action"] = None
            with info_col:
                audit_icon = " ✅" if already_audited else ""
                # CDN badge
                cdn_html = ""
                if cdn:
                    if cdn.get("has_cdn"):
                        cdn_html = (
                            f'<span style="background:#E8F5E9;color:#1B5E20;padding:2px 8px;'
                            f'border-radius:4px;font-size:11px;font-weight:600;margin-left:6px;">'
                            f'✓ {cdn.get("cdn_name","CDN")}</span>'
                        )
                    else:
                        cdn_html = (
                            f'<span style="background:#FEF2F2;color:#B91C1C;padding:2px 8px;'
                            f'border-radius:4px;font-size:11px;font-weight:600;margin-left:6px;">'
                            f'🔥 No CDN — hot lead</span>'
                        )
                st.markdown(
                    f"**{name}**{audit_icon} {cdn_html}",
                    unsafe_allow_html=True,
                )
                st.caption(f"[{url}]({url})  ·  *{src}*")
                if snip:
                    st.caption(snip[:160])
                if t:
                    st.markdown(_render_tech_badges(t), unsafe_allow_html=True)
                # Opportunity score badge (only if audited)
                if already_audited:
                    a = st.session_state.get("audits", {}).get(url, {})
                    opp = varnish_opportunity_score(a)
                    lbl, col = opportunity_label(opp)
                    spd = (a.get("breakdown") or {}).get("speed", {}).get("score", "—")
                    perf = (a.get("breakdown") or {}).get("performance", {}).get("score", "—")
                    st.markdown(
                        f'<div style="margin-top:4px;">'
                        f'<span style="background:{col}22;color:{col};padding:3px 10px;'
                        f'border-radius:4px;font-size:11px;font-weight:700;">'
                        f'{lbl} &nbsp;·&nbsp; Opp: {opp}/100 &nbsp;·&nbsp; Speed: {spd}/100 &nbsp;·&nbsp; Perf: {perf}/100'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )
            with btn_col:
                if AUDIT_AVAILABLE:
                    btn_label = (
                        f"✅ {_t('Re-check', 'Erneut prüfen')}" if already_audited
                        else f"🚀 {_t('Check', 'Prüfen')}"
                    )
                    if st.button(btn_label, key=f"audit_{idx}", use_container_width=True):
                        st.session_state["audits"].pop(url, None)
                        with st.spinner(f"{_t('Checking', 'Prüfe')} {url}…"):
                            result = audit_website(url)
                        st.session_state["audits"][url] = result
                        st.rerun()
        st.divider()

    # ── Bulk Audit ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="step-pill">{_t("Step 3", "Schritt 3")} &nbsp;·&nbsp; {_t("Check selected websites", "Ausgewählte Websites prüfen")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"#### {_t('Check all the ones you picked', 'Alle ausgewählten prüfen')}")
    n_selected = len(selected)

    if n_selected == 0:
        st.info(_t(
            "☝ Tick the boxes next to the businesses above, then click the button below to check them all at once.",
            "☝ Setzen Sie oben Häkchen bei den Unternehmen und klicken Sie dann unten auf die Schaltfläche.",
        ))
    else:
        site_word = _t("website", "Website") if n_selected == 1 else _t("websites", "Websites")
        st.success(f"**{n_selected}** {site_word} {_t('selected — ready to check!', 'ausgewählt — bereit zur Prüfung!')}")

    audit_selected_btn = st.button(
        f"🚀 {_t('Check', 'Prüfe')} {n_selected} {_t('website', 'Website') if n_selected == 1 else _t('websites', 'Websites')}",
        type="primary",
        use_container_width=True,
        disabled=(n_selected == 0),
    )

    if audit_selected_btn and n_selected > 0:
        prog   = st.progress(0, text=_t("Starting…", "Wird gestartet…"))
        status = st.empty()
        batch  = [url for url in selected if url]
        for i, url in enumerate(batch):
            status.info(f"🔍 {_t('Checking', 'Prüfe')} **{i+1}/{len(batch)}**: {url}")
            with st.spinner(f"{_t('Working on', 'Bearbeite')} {url}…"):
                result = audit_website(url)
            st.session_state["audits"][url] = result
            prog.progress(
                (i + 1) / len(batch),
                text=f"{_t('Done', 'Fertig')}: {i+1} / {len(batch)}",
            )
        status.empty(); prog.empty()
        sites_done = len(batch)
        site_word  = _t("website", "Website") if sites_done == 1 else _t("websites", "Websites")
        st.success(f"✅ {_t('All done!', 'Alles fertig!')} {sites_done} {site_word} {_t('checked.', 'geprüft.')}")
        st.rerun()

# ── STEP 3 / 4: Audit Results ─────────────────────────────────────────────────
audits = st.session_state.get("audits", {})
_direct_mode_results = audits and "results" not in st.session_state

if audits:
    step_label = (
        _t("Step 4", "Schritt 4") if "results" in st.session_state
        else _t("Step 3", "Schritt 3")
    )
    st.markdown(
        f'<div class="step-pill">{step_label} &nbsp;·&nbsp; {_t("Audit Results", "Prüfergebnisse")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"#### {_t('Audit Results', 'Prüfergebnisse')}")
    audit_list = list(audits.values())

    if not _direct_mode_results:
        successful = [a for a in audit_list if not a.get("error")]
        scores     = [a.get("overall_score", 0) for a in successful]
        opps       = [varnish_opportunity_score(a) for a in successful]

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric(_t("Sites Audited", "Geprüfte Seiten"), len(successful))
        with mc2: st.metric(_t("Avg Score", "Ø Score"), f"{int(sum(scores)/len(scores)) if scores else 0}/100")
        with mc3: st.metric(_t("Hot Leads (opp ≥ 75)", "Heiße Leads"), sum(1 for o in opps if o >= 75))
        with mc4: st.metric(_t("Avg Opportunity", "Ø Opportunity"), f"{int(sum(opps)/len(opps)) if opps else 0}/100")

        only_poor = st.checkbox(_t("Show only high-opportunity sites (opp ≥ 50)", "Nur hochopportune Seiten anzeigen (Opp ≥ 50)"))
        filtered  = [a for a in audit_list if not only_poor or (not a.get("error") and varnish_opportunity_score(a) >= 50)]
    else:
        filtered = audit_list

    # ── Contact extraction state ──────────────────────────────────────────────
    if "contacts" not in st.session_state:
        st.session_state["contacts"] = {}
    contacts = st.session_state["contacts"]

    # ── Bulk contact extraction button ────────────────────────────────────────
    if CONTACT_AVAILABLE:
        pending_contact = [
            a.get("url", "") for a in filtered
            if not a.get("error") and a.get("url", "") not in contacts
        ]
        if pending_contact:
            if st.button(
                f"📧 {_t('Extract contact info for all audited sites', 'Kontaktdaten aller geprüften Seiten extrahieren')} ({len(pending_contact)} {_t('sites', 'Seiten')})",
                use_container_width=True,
            ):
                prog   = st.progress(0)
                status = st.empty()
                for i, url in enumerate(pending_contact):
                    status.text(f"{_t('Extracting contacts from', 'Extrahiere Kontakte von')} {url}…")
                    contacts[url] = extract_contact_info(url)
                    st.session_state["contacts"] = contacts
                    prog.progress((i + 1) / len(pending_contact))
                status.empty(); prog.empty()
                st.success(_t("Contact extraction complete!", "Kontaktextraktion abgeschlossen!"))
                st.rerun()

    # ── Individual audit cards ────────────────────────────────────────────────
    for a in filtered:
        url   = a.get("url", "")
        score = a.get("overall_score", 0)
        bd    = a.get("breakdown", {})
        fetch_err = a.get("error", "")
        opp   = varnish_opportunity_score(a) if not fetch_err else 0
        opp_lbl, opp_col = opportunity_label(opp)

        expander_title = (
            f"⚠️ {url}  — Could not reach site"
            if fetch_err else
            f"{'🟢' if score >= 70 else '🟡' if score >= 50 else '🔴'} "
            f"{url}  —  {score}/100  ·  {opp_lbl} ({opp}/100)"
        )

        with st.expander(expander_title, expanded=_direct_mode_results):
            if fetch_err:
                st.error(
                    f"❌ **Could not audit this site.**\n\n"
                    f"{fetch_err}\n\n"
                    f"Please verify the URL is correct and the site is publicly accessible, then try again."
                )
                continue

            # ── Feature 6: Varnish Opportunity Score banner ───────────────────
            st.markdown(
                f'<div style="background:{opp_col}15;border:1.5px solid {opp_col}44;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:14px;'
                f'display:flex;align-items:center;gap:16px;">'
                f'<div style="text-align:center;min-width:70px;">'
                f'<div style="font-size:2rem;font-weight:800;color:{opp_col};">{opp}</div>'
                f'<div style="font-size:10px;font-weight:700;color:{opp_col};text-transform:uppercase;'
                f'letter-spacing:.05em;">OPPORTUNITY</div></div>'
                f'<div><div style="font-size:13px;font-weight:700;color:{opp_col};">{opp_lbl}</div>'
                f'<div style="font-size:11px;color:#6B7A99;margin-top:2px;">'
                f'Speed: <b>{(lambda v: v if not isinstance(v, dict) else "—")((bd.get("speed") or {}).get("score", "—"))}/100</b> &nbsp;·&nbsp; '
                f'Performance: <b>{(lambda v: v if not isinstance(v, dict) else "—")((bd.get("performance") or {}).get("score", "—"))}/100</b> &nbsp;·&nbsp; '
                f'{"🔥 No CDN detected — hot lead for Varnish cache" if not st.session_state.get("cdn_map", {}).get(url, {}).get("has_cdn") else "✓ CDN already detected"}'
                f'</div>'
                f'<div style="font-size:11px;color:#9AA5BC;margin-top:3px;">'
                f'{"A high Opportunity score means this site is slow and would benefit most from Varnish Edge Cache." if opp >= 50 else "This site already has decent performance — lower priority for outreach."}'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

            # ── Feature 1: Speed / caching context callout ────────────────────
            spd_score = (bd.get("speed") or {}).get("score", 50)
            prf_score = (bd.get("performance") or {}).get("score", 50)
            proj      = a.get("fastsite_projection") or {}
            cur       = proj.get("current", {})
            prj_d     = proj.get("projected", {})
            if spd_score < 60 or prf_score < 60:
                ttfb_now  = cur.get("ttfb_ms")
                ttfb_proj = prj_d.get("ttfb_ms")
                ps_min    = prj_d.get("perf_score_min")
                ps_max    = prj_d.get("perf_score_max")
                ttfb_line = (
                    f"Server response time is **{ttfb_now}ms** — ideal is under 200ms. "
                    f"Varnish Edge Cache would bring this to **~{ttfb_proj}ms**."
                    if ttfb_now and ttfb_proj
                    else ""
                )
                ps_line = (
                    f"PageSpeed score could jump from **{prf_score}** to **{ps_min}–{ps_max}/100**."
                    if ps_min else ""
                )
                st.info(
                    f"⚡ **Why this matters for fast.site:**  "
                    f"This site loads slowly — it's losing customers and ranking lower in Google.  "
                    f"{ttfb_line}  {ps_line}  "
                    f"Varnish Cache could reduce load times by 3–10× with a single DNS switch. "
                    f"No code changes required. Active within 24 hours."
                )

            # ── Score breakdown ───────────────────────────────────────────────
            st.markdown(
                f'<div style="height:10px;background:#E5EAF3;border-radius:99px;margin-bottom:16px;overflow:hidden;">'
                f'<div style="height:10px;width:{score}%;background:{_score_color(score)};border-radius:99px;transition:width 0.6s ease;"></div>'
                f'</div>', unsafe_allow_html=True
            )

            if bd:
                cols = st.columns(len(bd))
                for col, (cat, data) in zip(cols, bd.items()):
                    s = data.get("score", 0)
                    # Highlight Speed and Performance specially
                    highlight = cat in ("speed", "performance")
                    border_col = "#2563EB" if highlight else "#E5EAF3"
                    col.markdown(
                        f'<div style="text-align:center;background:#F7F8FA;border:{"2px" if highlight else "1px"} solid {border_col};'
                        f'border-radius:10px;padding:0.85rem 0.5rem;">'
                        f'<div style="font-size:1.6rem;font-weight:700;color:{_score_color(s)};line-height:1;">{s}</div>'
                        f'<div style="font-size:10px;color:{"#2563EB" if highlight else "#6B7A99"};font-weight:{"700" if highlight else "600"};letter-spacing:0.07em;'
                        f'text-transform:uppercase;margin-top:4px;">{cat}</div></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")

            # ── Feature 2: Contact info ───────────────────────────────────────
            contact = contacts.get(url, {})
            if contact:
                st.markdown(f"**📧 {_t('Contact Info', 'Kontaktdaten')}**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    em = contact.get("primary_email")
                    st.markdown(f"**Email:** `{em}`" if em else "**Email:** —")
                with c2:
                    ph = contact.get("phones", [])
                    st.markdown(f"**Phone:** `{ph[0]}`" if ph else "**Phone:** —")
                with c3:
                    cp = contact.get("contact_page")
                    if cp:
                        st.markdown(f"**Contact page:** [{cp}]({cp})")
                    else:
                        st.markdown("**Contact page:** —")
            elif CONTACT_AVAILABLE:
                if st.button(
                    f"📧 {_t('Extract contact info', 'Kontaktdaten extrahieren')}",
                    key=f"contact_{url}",
                ):
                    with st.spinner(_t("Scanning for contact info…", "Suche Kontaktdaten…")):
                        contacts[url] = extract_contact_info(url)
                        st.session_state["contacts"] = contacts
                    st.rerun()

            # ── Feature 5: Cold email generator ───────────────────────────────
            contact = contacts.get(url, {})  # refresh after possible extraction
            with st.expander(f"✉️ {_t('Generate cold email for this site', 'Kalt-E-Mail generieren')}"):
                import re as _re
                m = _re.search(r"https?://(?:www\.)?([^/]+)", url)
                biz_name = m.group(1) if m else url
                cdn_info = st.session_state.get("cdn_map", {}).get(url, {})
                email_text = generate_cold_email(
                    business_name=biz_name,
                    url=url,
                    overall_score=score,
                    speed_score=spd_score,
                    performance_score=prf_score,
                    opportunity_score=opp,
                    primary_email=contact.get("primary_email"),
                    ttfb_ms=cur.get("ttfb_ms"),
                    lcp_ms=cur.get("lcp_ms"),
                    has_cdn=cdn_info.get("has_cdn", False),
                )
                st.text_area(
                    _t("Cold email (copy and personalise)", "Kalt-E-Mail (kopieren & anpassen)"),
                    value=email_text,
                    height=340,
                    key=f"email_{url}",
                )
                st.download_button(
                    f"⬇ {_t('Download email as .txt', 'E-Mail als .txt herunterladen')}",
                    data=email_text.encode(),
                    file_name=f"cold_email_{biz_name}.txt",
                    mime="text/plain",
                    key=f"dl_email_{url}",
                )

            st.markdown("---")
            try:
                pdf_bytes = generate_audit_pdf(a, lang=_LANG)
                safe      = url.replace("https://", "").replace("http://", "").replace("/", "_").strip("_")
                st.download_button(
                    f"⬇ {_t('Download Audit Report (PDF)', 'Prüfbericht herunterladen (PDF)')}",
                    data=pdf_bytes,
                    file_name=f"audit_{safe}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_{url}",
                )
            except Exception as e:
                st.warning(f"{_t('PDF generation failed', 'PDF-Erstellung fehlgeschlagen')}: {e}")

    # ── Export section ────────────────────────────────────────────────────────
    st.markdown(f"#### {_t('Export Lead Data', 'Lead-Daten exportieren')}")
    exp_col1, exp_col2 = st.columns(2)

    # Feature 4: CSV export
    with exp_col1:
        cdn_map_data = st.session_state.get("cdn_map", {})
        csv_bytes = build_leads_csv(
            audit_results=[a for a in filtered if not a.get("error")],
            contact_data=contacts,
            cdn_data=cdn_map_data,
        )
        st.download_button(
            f"⬇ {_t('Export Leads as CSV', 'Leads als CSV exportieren')} ({len([a for a in filtered if not a.get('error')])} {_t('sites', 'Seiten')})",
            data=csv_bytes,
            file_name="fastsite_leads.csv",
            mime="text/csv",
            use_container_width=True,
            key="csv_export",
        )
        st.caption(_t(
            "Includes: business name, URL, email, phone, scores, CDN status, TTFB, LCP",
            "Enthält: Unternehmensname, URL, E-Mail, Telefon, Scores, CDN-Status, TTFB, LCP"
        ))

    # Bulk PDF
    with exp_col2:
        writer = PdfWriter()
        for a in filtered:
            if a.get("error"):
                continue
            try:
                pdf_bytes = generate_audit_pdf(a, lang=_LANG)
                writer.append(io.BytesIO(pdf_bytes))
            except Exception:
                pass
        if writer.pages:
            buf = io.BytesIO()
            writer.write(buf)
            buf.seek(0)
            st.download_button(
                f"⬇ {_t('Download All Reports (PDF)', 'Alle Berichte herunterladen (PDF)')}",
                data=buf.read(),
                file_name=_t("fastsite_leads_reports.pdf", "fastsite_leads_berichte.pdf"),
                mime="application/pdf",
                use_container_width=True,
                key="pdf_bulk",
            )
        else:
            st.info(_t("Run audits first to generate PDF reports.",
                       "Führen Sie zuerst Prüfungen durch, um PDF-Berichte zu erstellen."))

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-footer">
  fast.site Lead Finder &nbsp;·&nbsp; {_t(
      "Find slow sites · Contact extraction · Cold email generation · CSV export · PDF reports",
      "Langsame Seiten finden · Kontakte extrahieren · E-Mails generieren · CSV · PDF"
  )}
</div>
""", unsafe_allow_html=True)