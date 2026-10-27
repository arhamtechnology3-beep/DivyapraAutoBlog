#!/usr/bin/env python3
"""
GSC first-wave SEO apply script for divyaprabhafoods.com

Updates (Admin API):
  1. Gor Keri keeper article — title, SEO, opening answer + product CTA
  2. Five money collections — SEO title, meta, intro-only description
  3. Four product pages — SEO title + meta
  4. Two high-impression blogs — shorter title + meta

Usage:
  export SHOPIFY_ACCESS_TOKEN=shpat_...
  python3 scratch/gsc_first_wave_seo.py            # apply
  python3 scratch/gsc_first_wave_seo.py --dry-run  # print payloads only
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

SHOP_URL = os.environ.get("SHOPIFY_SHOP_URL", "https://divyaprabhafoods.myshopify.com").rstrip("/")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
BLOG_ID = int(os.environ.get("SHOPIFY_BLOG_ID", "97942077654"))
API = "2024-04"
CTX = ssl.create_default_context()

GOR_KERI_PRODUCT = "/products/gor-keri-pickle-jaggery-mango-achar-gujarati"
GOR_KERI_IMAGE = (
    "https://cdn.shopify.com/s/files/1/0752/0904/8278/files/Gor_Keri_500g.webp?v=1784831601"
)

# --- Copy (titles ≤60 with Divyaprabha Foods; metas 150–160) ---

ARTICLES = {
    "gorkeri-pickle-health": {
        "id": 666456096982,
        "title": "Gor Keri Meaning: Sweet Jaggery Mango Pickle",
        "seo_title": "Gor Keri Meaning: Jaggery Mango | Divyaprabha Foods",
        "seo_desc": (
            "Gor Keri means sweet jaggery mango pickle from Saurashtra. "
            "Learn how Divyaprabha Foods sun-cures traditional Gor Keri achar — buy the jar online today."
        ),
        "prepend_answer": True,
    },
    "top-10-homemade-pickles-in-india": {
        "id": 665621692630,
        "title": "Top 10 Homemade Pickles in India",
        "seo_title": "Top 10 Homemade Pickles in India | Divyaprabha Foods",
        "seo_desc": (
            "Compare 10 homemade Indian pickles — mango, Gor Keri, Methia Keri and more. "
            "See what makes Divyaprabha Foods jars different, then shop authentic achar."
        ),
        "prepend_answer": False,
    },
    "are-traditional-indian-pickles-good-for-gut-health-the-hidden-probiotic-benefits-of-sun-cured-achaar": {
        "id": 665915687126,
        "title": "Are Traditional Indian Pickles Worth It?",
        "seo_title": "Are Traditional Indian Pickles Worth It? | Divyaprabha Foods",
        "seo_desc": (
            "Curious about traditional Indian pickles? Learn how Divyaprabha Foods "
            "sun-cures Saurashtra achar with real spices — no preservatives — and shop the jars."
        ),
        "prepend_answer": False,
    },
}

COLLECTIONS = {
    # try custom first, then smart
    "pickles": {
        "id": 477558571222,
        "seo_title": "Buy Gujarati Pickles Online | Divyaprabha Foods",
        "seo_desc": (
            "Buy authentic Gujarati pickles online from Divyaprabha Foods. "
            "Homemade Saurashtra achar — Gor Keri, Methia Keri, Gunda Keri. No preservatives. Shop now."
        ),
        "body_html": (
            "<p><strong>Gujarati pickles</strong> from Divyaprabha Foods are small-batch "
            "Saurashtra achar made with Baa's recipe since 1980 — Gor Keri, Methia Keri, "
            "Gunda Keri, and more. No vinegar, no sodium benzoate; 12-month shelf life.</p>"
            "<p>Shop the jars below, or start with "
            f'<a href="{GOR_KERI_PRODUCT}">Gor Keri (jaggery mango achar)</a>.</p>'
        ),
    },
    "best-pickle-brands-in-india": {
        "id": 479915802838,
        "seo_title": "Best Pickle Brands in India | Divyaprabha Foods",
        "seo_desc": (
            "Looking for the best pickle brands in India? Taste Divyaprabha Foods "
            "homemade Gujarati achar — small-batch, FSSAI-certified, shipped fresh. Shop today."
        ),
        "body_html": (
            "<p>Shoppers comparing the <strong>best pickle brands in India</strong> want "
            "clear ingredients and a real regional recipe. Divyaprabha Foods makes "
            "homemade Gujarati achar in Saurashtra — small batches, no preservatives.</p>"
            "<p>Browse the collection below, or go straight to "
            f'<a href="{GOR_KERI_PRODUCT}">Gor Keri</a> and '
            '<a href="/products/mango-pickle-traditional-keri-achar-gujarati">traditional mango pickle</a>.</p>'
        ),
    },
    "tangyspicy-pickle": {
        "id": 458051027158,
        "seo_title": "Tangy Spicy Pickles Online | Divyaprabha Foods",
        "seo_desc": (
            "Shop tangy spicy Gujarati pickles online from Divyaprabha Foods. Homemade "
            "Saurashtra achar with bold spice — no preservatives. Order fresh jars today."
        ),
        "body_html": (
            "<p><strong>Tangy spicy pickles</strong> from Divyaprabha Foods bring "
            "Saurashtra heat and sour mango bite — Methia Keri, Gunda Keri, and classic "
            "mango achar. Mustard or peanut oil by recipe; never palm oil or vinegar.</p>"
            '<p>Order from the jars below, including '
            '<a href="/products/chana-keri-methi-pickle-gujarati-methia-achar">Methia Keri</a>.</p>'
        ),
    },
    "homemade-pickles": {
        "id": 479913410774,
        "seo_title": "Homemade Pickles Online | Divyaprabha Foods",
        "seo_desc": (
            "Buy homemade pickles online from Divyaprabha Foods. Traditional Gujarati "
            "and Saurashtra achar, small-batch, no preservatives. Fresh jars shipped to you."
        ),
        "body_html": (
            "<p><strong>Homemade pickles</strong> at Divyaprabha Foods follow Baa's "
            "Saurashtra kitchen method: hand-cut fruit, sun-curing, and spice by spice — "
            "not factory vinegar brine. Shelf life 12 months when kept dry and cool.</p>"
            f'<p>Start with <a href="{GOR_KERI_PRODUCT}">Gor Keri</a> or '
            '<a href="/products/mango-pickle-traditional-keri-achar-gujarati">aam ka achar</a>.</p>'
        ),
    },
    "organic-pickles": {
        "id": 479913083094,
        "seo_title": "Natural Pickles Online | Divyaprabha Foods",
        "seo_desc": (
            "Shop natural Gujarati pickles made with traditional Saurashtra recipes. "
            "No preservatives, small-batch achar from Divyaprabha Foods. Order online today."
        ),
        "body_html": (
            "<p>Looking for <strong>natural pickles</strong> without synthetic preservatives? "
            "Divyaprabha Foods jars use traditional Saurashtra recipes — no sodium benzoate, "
            "no vinegar, no palm oil. We do not claim certified-organic status.</p>"
            "<p>Shop the collection below for small-batch Gujarati achar shipped from our kitchen.</p>"
        ),
    },
}

PRODUCTS = {
    "gor-keri-pickle-jaggery-mango-achar-gujarati": {
        "id": 9374511202518,
        "seo_title": "Gor Keri Pickle | Jaggery Mango | Divyaprabha Foods",
        "seo_desc": (
            "Buy Gor Keri pickle online — sweet jaggery mango achar from Divyaprabha Foods. "
            "Peanut-oil cured, no preservatives. Traditional Saurashtra recipe. Shop now."
        ),
    },
    "sweet-mango-pickle-meethi-keri-achar-homemade": {
        "id": 9374511038678,
        "seo_title": "Meethi Keri | Sweet Mango Pickle | Divyaprabha Foods",
        "seo_desc": (
            "Buy Meethi Keri sweet mango pickle online from Divyaprabha Foods. "
            "Sugar-sweetened, no added oil, no preservatives. Traditional Gujarati achar. Shop today."
        ),
    },
    "chana-keri-methi-pickle-gujarati-methia-achar": {
        "id": 9374511071446,
        "seo_title": "Methia Keri | Chana Methi Pickle | Divyaprabha Foods",
        "seo_desc": (
            "Buy Methia Keri (Chana Keri Methi) pickle online from Divyaprabha Foods. "
            "Mustard-oil achar with mango, chana and methi. No preservatives. Order yours now."
        ),
    },
    "mango-pickle-traditional-keri-achar-gujarati": {
        "id": 9374511104214,
        "seo_title": "Mango Pickle Online | Keri Achar | Divyaprabha Foods",
        "seo_desc": (
            "Buy traditional mango pickle (keri achar) online from Divyaprabha Foods. "
            "Peanut-oil cured Gujarati aam ka achar, no preservatives. Order your jar today."
        ),
    },
}

GOR_KERI_OPENING = f"""
<p><strong>Gor Keri</strong> means sweet jaggery mango pickle — raw mango cured with gur (jaggery) in the Gujarati / Saurashtra style. At Divyaprabha Foods, Gor Keri is peanut-oil cured, made in small batches from Baa's recipe since 1980, with no vinegar and no sodium benzoate.</p>
<p>If you searched <em>gorkeri means</em> or <em>gorkeri pickle meaning</em>, you are looking for that sweet–tangy jar, not a spicy mustard achar. Below is how we make it, and how it differs from Chhundo and Meethi Keri.</p>
<div class="dp-product-card" style="background:#fdf6ed;border:1px solid #e8d5c0;border-radius:16px;padding:24px;margin:32px 0;text-align:center;box-shadow:0 4px 12px rgba(61,31,15,0.05);">
  <img src="{GOR_KERI_IMAGE}" alt="Gor Keri jaggery mango pickle jar - Divyaprabha Foods" style="max-width:240px;width:100%;height:auto;border-radius:12px;margin-bottom:16px;">
  <h3 style="color:#b01215;margin:8px 0 12px 0;font-size:20px;">Gor Keri | Jaggery Mango Achar</h3>
  <p style="color:#3d1f0f;font-size:14px;margin-bottom:16px;">Sweet jaggery mango achar, peanut-oil cured in Saurashtra. No vinegar, no preservatives.</p>
  <a href="{GOR_KERI_PRODUCT}" style="background:#b01215;color:#ffffff;padding:12px 32px;border-radius:50px;font-weight:bold;text-decoration:none;display:inline-block;">Buy Authentic Gor Keri Online →</a>
</div>
""".strip()

MARKER = "<!-- GSC-FIRST-WAVE:GOR-KERI-ANSWER -->"


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


def ensure_token() -> None:
    if not TOKEN or TOKEN.startswith("os.environ"):
        raise SystemExit(
            "Set SHOPIFY_ACCESS_TOKEN first.\n"
            "  export SHOPIFY_ACCESS_TOKEN='shpat_...'"
        )


def validate_copy() -> None:
    for label, text, lo, hi in [
        *((f"article:{h}:seo_title", a["seo_title"], 1, 60) for h, a in ARTICLES.items()),
        *((f"article:{h}:seo_desc", a["seo_desc"], 150, 160) for h, a in ARTICLES.items()),
        *((f"collection:{h}:seo_title", c["seo_title"], 1, 60) for h, c in COLLECTIONS.items()),
        *((f"collection:{h}:seo_desc", c["seo_desc"], 150, 160) for h, c in COLLECTIONS.items()),
        *((f"product:{h}:seo_title", p["seo_title"], 1, 60) for h, p in PRODUCTS.items()),
        *((f"product:{h}:seo_desc", p["seo_desc"], 150, 160) for h, p in PRODUCTS.items()),
    ]:
        n = len(text)
        if n < lo or n > hi:
            raise SystemExit(f"Copy length fail {label}: {n} (want {lo}-{hi})\n{text}")


def update_articles(dry_run: bool) -> None:
    for handle, cfg in ARTICLES.items():
        art_id = cfg["id"]
        path = f"blogs/{BLOG_ID}/articles/{art_id}.json"
        print(f"ARTICLE {handle}: title={cfg['title']!r} seo={len(cfg['seo_title'])}/{len(cfg['seo_desc'])}")
        if dry_run:
            continue
        current = request("GET", path)["article"]
        body = current.get("body_html") or ""
        if cfg.get("prepend_answer"):
            end = "<!-- /GSC-FIRST-WAVE:GOR-KERI-ANSWER -->"
            if MARKER in body and end in body:
                pre = body.split(MARKER, 1)[0]
                post = body.split(end, 1)[1]
                body = pre + post
            block = f"{MARKER}\n{GOR_KERI_OPENING}\n{end}\n"
            body = block + body
        payload = {
            "article": {
                "id": art_id,
                "title": cfg["title"],
                "body_html": body,
                "metafields_global_title_tag": cfg["seo_title"],
                "metafields_global_description_tag": cfg["seo_desc"],
            }
        }
        request("PUT", path, payload)
        print(f"  ✓ updated article {art_id}")


def update_collections(dry_run: bool) -> None:
    for handle, cfg in COLLECTIONS.items():
        cid = cfg["id"]
        payload_custom = {
            "custom_collection": {
                "id": cid,
                "body_html": cfg["body_html"],
                "metafields_global_title_tag": cfg["seo_title"],
                "metafields_global_description_tag": cfg["seo_desc"],
            }
        }
        payload_smart = {
            "smart_collection": {
                "id": cid,
                "body_html": cfg["body_html"],
                "metafields_global_title_tag": cfg["seo_title"],
                "metafields_global_description_tag": cfg["seo_desc"],
            }
        }
        print(f"COLLECTION {handle}: seo={cfg['seo_title']!r}")
        if dry_run:
            continue
        try:
            request("PUT", f"custom_collections/{cid}.json", payload_custom)
            print(f"  ✓ custom_collection {cid}")
        except RuntimeError as e:
            if "404" not in str(e):
                raise
            try:
                request("PUT", f"smart_collections/{cid}.json", payload_smart)
                print(f"  ✓ smart_collection {cid}")
            except RuntimeError as e2:
                # Some storefront collections are not writable via Admin REST for this
                # app; theme SERP overrides in layout/theme.liquid still apply.
                print(f"  ⚠ skipped Admin collection update ({handle}): {e2}")


def update_products(dry_run: bool) -> None:
    for handle, cfg in PRODUCTS.items():
        pid = cfg["id"]
        payload = {
            "product": {
                "id": pid,
                "metafields_global_title_tag": cfg["seo_title"],
                "metafields_global_description_tag": cfg["seo_desc"],
            }
        }
        print(f"PRODUCT {handle}: seo={cfg['seo_title']!r}")
        if dry_run:
            continue
        request("PUT", f"products/{pid}.json", payload)
        print(f"  ✓ updated product {pid}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    validate_copy()
    if not args.dry_run:
        ensure_token()
    print(f"Shop={SHOP_URL} dry_run={args.dry_run}")
    update_articles(args.dry_run)
    update_collections(args.dry_run)
    update_products(args.dry_run)
    print("Done.")


if __name__ == "__main__":
    main()
