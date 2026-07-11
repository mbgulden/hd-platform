"""
Printful fulfillment helpers for HDE/AOT print-on-demand products.

This module is intentionally dependency-free so the lightweight payment server can
submit paid Stripe Checkout sessions to Printful without adding a web framework or
SDK. It uses Printful's JSON Orders API shape:

POST https://api.printful.com/orders?confirm=<true|false>
{
  "external_id": "cs_...",
  "recipient": {...},
  "items": [{"variant_id": 123, "quantity": 1, "files": [{"url": "..."}]}]
}
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

DEFAULT_MAPPING_PATH = Path(__file__).resolve().parent.parent / "data" / "shop" / "printful-mapping.json"


class PrintfulConfigurationError(RuntimeError):
    """Raised when a paid print order cannot be submitted due to config."""


class PrintfulAPIError(RuntimeError):
    """Raised when Printful rejects an order request."""


@dataclass(frozen=True)
class PrintfulVariant:
    sku: str
    variant_id: int
    product_id: Optional[int]
    retail_price: str
    size: str
    format: str = "poster"


def load_variant_mapping(path: Optional[str] = None) -> Dict[str, PrintfulVariant]:
    """Load SKU -> Printful variant mapping from JSON.

    The committed mapping contains placeholder variant IDs for local/test mode.
    Production must set real Printful variant IDs before enabling confirmed orders.
    """

    mapping_path = Path(path or os.environ.get("PRINTFUL_MAPPING_PATH", DEFAULT_MAPPING_PATH))
    if not mapping_path.exists():
        raise PrintfulConfigurationError(f"Printful mapping file not found: {mapping_path}")

    raw = json.loads(mapping_path.read_text())
    variants: Dict[str, PrintfulVariant] = {}
    for sku, item in raw.items():
        variant_id = int(item.get("printful_variant_id") or 0)
        variants[sku] = PrintfulVariant(
            sku=sku,
            variant_id=variant_id,
            product_id=item.get("printful_product_id"),
            retail_price=str(item.get("retail_price", "0.00")),
            size=str(item.get("size", "")),
            format=str(item.get("format", "poster")),
        )
    return variants


def is_print_order(metadata: Mapping[str, Any]) -> bool:
    report = str(metadata.get("report") or metadata.get("product") or "").lower()
    product_type = str(metadata.get("product_type") or "").lower()
    return product_type == "print" or report in {"poster", "print-poster", "poster-print"}


def poster_sku(size: str) -> str:
    normalized = (size or "18x24").lower().replace("×", "x").replace(" ", "")
    return f"poster_{normalized}"


def variant_for_metadata(metadata: Mapping[str, Any]) -> PrintfulVariant:
    sku = metadata.get("printful_sku") or poster_sku(str(metadata.get("poster_size") or metadata.get("size") or "18x24"))
    variants = load_variant_mapping()
    try:
        variant = variants[str(sku)]
    except KeyError as exc:
        raise PrintfulConfigurationError(f"No Printful variant mapping for SKU {sku!r}") from exc
    if variant.variant_id <= 0:
        raise PrintfulConfigurationError(f"Printful variant ID is not configured for SKU {sku!r}")
    return variant


def _session_value(session: Mapping[str, Any], *keys: str) -> str:
    value: Any = session
    for key in keys:
        if not isinstance(value, Mapping):
            return ""
        value = value.get(key)
    return str(value or "")


def recipient_from_session(session: Mapping[str, Any]) -> Dict[str, str]:
    """Extract Printful recipient from a Stripe Checkout Session object."""

    shipping = session.get("shipping_details") or {}
    customer = session.get("customer_details") or {}
    address = shipping.get("address") or customer.get("address") or {}

    recipient = {
        "name": str(shipping.get("name") or customer.get("name") or session.get("customer_email") or "").strip(),
        "email": str(customer.get("email") or session.get("customer_email") or "").strip(),
        "address1": str(address.get("line1") or "").strip(),
        "address2": str(address.get("line2") or "").strip(),
        "city": str(address.get("city") or "").strip(),
        "state_code": str(address.get("state") or "").strip(),
        "country_code": str(address.get("country") or "US").strip() or "US",
        "zip": str(address.get("postal_code") or "").strip(),
    }

    missing = [key for key in ("name", "address1", "city", "country_code", "zip") if not recipient.get(key)]
    if missing:
        raise PrintfulConfigurationError(
            "Stripe Checkout Session is missing shipping fields required by Printful: " + ", ".join(missing)
        )
    return recipient


def build_order_payload(session: Mapping[str, Any]) -> Dict[str, Any]:
    metadata = session.get("metadata") or {}
    variant = variant_for_metadata(metadata)
    file_url = str(metadata.get("print_file_url") or metadata.get("poster_image_url") or "").strip()
    if not file_url:
        raise PrintfulConfigurationError("Missing print_file_url/poster_image_url metadata for Printful order")

    external_id = str(session.get("id") or metadata.get("stripe_session_id") or "").strip()
    if not external_id:
        raise PrintfulConfigurationError("Missing Stripe session id for Printful external_id")

    return {
        "external_id": external_id,
        "shipping": str(os.environ.get("PRINTFUL_SHIPPING_METHOD", "STANDARD")),
        "recipient": recipient_from_session(session),
        "items": [
            {
                "variant_id": variant.variant_id,
                "quantity": int(metadata.get("quantity") or 1),
                "retail_price": variant.retail_price,
                "name": f"Human Design Engine Poster — {variant.size}",
                "files": [{"url": file_url}],
            }
        ],
    }


def create_order(session: Mapping[str, Any], *, confirm: Optional[bool] = None) -> Dict[str, Any]:
    """Submit a paid Stripe Checkout Session to Printful.

    By default this creates draft Printful orders (`PRINTFUL_CONFIRM_ORDERS=false`).
    Set PRINTFUL_CONFIRM_ORDERS=true only after mapping IDs and artwork URLs are
    verified in live/test Printful.
    """

    token = os.environ.get("PRINTFUL_API_TOKEN") or os.environ.get("PRINTFUL_TOKEN")
    if not token:
        raise PrintfulConfigurationError("PRINTFUL_API_TOKEN is not configured")

    if confirm is None:
        confirm = os.environ.get("PRINTFUL_CONFIRM_ORDERS", "false").lower() == "true"

    payload = build_order_payload(session)
    query = urllib.parse.urlencode({"confirm": "true" if confirm else "false"})
    req = urllib.request.Request(
        f"https://api.printful.com/orders?{query}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    store_id = os.environ.get("PRINTFUL_STORE_ID")
    if store_id:
        req.add_header("X-PF-Store-Id", store_id)

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        raise PrintfulAPIError(f"Printful API HTTP {exc.code}: {body[:500]}") from exc
