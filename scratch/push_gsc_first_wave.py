#!/usr/bin/env python3
"""
Push GSC first-wave theme assets to the live main theme, then apply Admin API SEO updates.

Requires:
  export SHOPIFY_ACCESS_TOKEN=shpat_...

Theme ID fallback from CHANGES.md: 161791869142 (Magic Checkout - ArhamFoods)
"""

from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOP_URL = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com").rstrip("/")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
KNOWN_THEME_ID = int(os.environ.get("SHOPIFY_THEME_ID", "161791869142"))
API = "2024-04"
CTX = ssl.create_default_context()

ASSETS = [
    "layout/theme.liquid",
    "sections/dp-article.liquid",
    "sections/main-article.liquid",
    "sections/custom-collection-with-filters.liquid",
]


def request(method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{SHOP_URL}/admin/api/{API}/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=CTX) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"{method} {path} → HTTP {e.code}: {err[:500]}") from e


def resolve_theme_id() -> int:
    try:
        themes = request("GET", "themes.json").get("themes") or []
        for t in themes:
            if t.get("role") == "main":
                print(f"Main theme: {t.get('name')} ({t['id']})")
                return int(t["id"])
        print("No main theme via API; using KNOWN_THEME_ID", KNOWN_THEME_ID)
    except Exception as e:
        print("Theme list failed:", e, "— using KNOWN_THEME_ID", KNOWN_THEME_ID)
    return KNOWN_THEME_ID


def push_assets(theme_id: int) -> None:
    for rel in ASSETS:
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"Missing asset file: {path}")
        value = path.read_text(encoding="utf-8")
        payload = {"asset": {"key": rel, "value": value}}
        request("PUT", f"themes/{theme_id}/assets.json", payload)
        print(f"  ✓ pushed {rel}")


def main() -> None:
    if not TOKEN or TOKEN.startswith("os.environ"):
        raise SystemExit("Set SHOPIFY_ACCESS_TOKEN first")
    theme_id = resolve_theme_id()
    print("Pushing theme assets…")
    push_assets(theme_id)
    print("Applying Admin API SEO updates…")
    rc = subprocess.call([sys.executable, str(ROOT / "scratch/gsc_first_wave_seo.py")])
    if rc != 0:
        raise SystemExit(rc)
    print("GSC first wave live.")


if __name__ == "__main__":
    main()
