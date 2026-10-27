#!/usr/bin/env python3
"""
Get a store Admin API access token (shpat_…) for Divyaprabha Partner apps.

Shopify Partner / Dev Dashboard apps do NOT show shpat_ in the UI.
Use Client Credentials grant with Client ID + Client secret from:
  dev.shopify.com → Apps → <app> → Settings → Credentials

Postman equivalent
------------------
Method: POST
URL:    https://divyaprabhafoods.myshopify.com/admin/oauth/access_token
Headers:
  Content-Type: application/x-www-form-urlencoded
  Accept: application/json
Body (x-www-form-urlencoded):
  grant_type     = client_credentials
  client_id      = <Client ID>
  client_secret  = <Client secret shpss_…>

Response JSON:
  access_token  → shpat_…   (use as X-Shopify-Access-Token)
  scope         → granted scopes
  expires_in    → usually ~86400 seconds (~24h) — re-run when expired

Then:
  export SHOPIFY_ACCESS_TOKEN='shpat_…'
  python3 scratch/push_gsc_first_wave.py

Usage:
  export SHOPIFY_CLIENT_ID=...
  export SHOPIFY_CLIENT_SECRET=shpss_...
  python3 scratch/shopify_get_access_token.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

SHOP = os.environ.get("SHOPIFY_SHOP", "divyaprabhafoods.myshopify.com").replace("https://", "").strip("/")
CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "").strip()


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit(
            "Set SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET "
            "(from Partner app Settings → Credentials)."
        )
    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    ).encode()
    req = urllib.request.Request(
        f"https://{SHOP}/admin/oauth/access_token",
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:500]}") from e

    token = body.get("access_token", "")
    print("access_token=", token)
    print("scope=", body.get("scope"))
    print("expires_in=", body.get("expires_in"))
    if not token.startswith("shpat_"):
        print("WARNING: expected shpat_ prefix", file=sys.stderr)


if __name__ == "__main__":
    main()
