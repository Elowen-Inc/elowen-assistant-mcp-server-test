#!/usr/bin/env python3
"""
MCP Server for Grocery Search with HTTP stream and CORS support
"""

import os
import csv
import base64
import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(title="Grocery Search MCP Server")

# 🔧 FIX: Add CORS middleware FIRST, before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Crucial: includes OPTIONS
    allow_headers=["*"],
    allow_origin_regex=".*",
)


# Constants
CSV_FILE = Path(__file__).parent / "grocery_data_feb_2025_ref.csv"
IMAGES_DIR = Path(__file__).parent / "product_images"

# Cache
_products_cache = None


# Pydantic models
class GrocerySearchRequest(BaseModel):
    main_item: str
    full_title: str


class GroceryItem(BaseModel):
    title: str
    similarity_score: int
    product_id: str
    brand: str
    description: Optional[str] = None
    package_sizing: Optional[str] = None
    price_current: str
    price_original: Optional[str] = None
    deal_text: Optional[str] = None
    inventory: Optional[str] = None
    image_base64: Optional[str] = None
    product_link: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[GroceryItem]
    query_main: str
    query_full: str


def load_products():
    """Load and cache products"""
    global _products_cache
    if _products_cache is not None:
        return _products_cache

    products = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)
        print(f"✓ Loaded {len(products)} products from CSV")
    except Exception as e:
        print(f"✗ Failed to load CSV: {e}")
        return []

    _products_cache = products
    return products


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    return (text or "").strip().lower()


def calculate_similarity(query: str, title: str) -> int:
    """Calculate similarity score (0-100)"""
    query_norm = normalize_text(query)
    title_norm = normalize_text(title)

    if query_norm == title_norm:
        return 100

    ratio = SequenceMatcher(None, query_norm, title_norm).ratio()
    return int(ratio * 100)


def format_price(product: dict) -> str:
    """Extract best available price"""
    for field in ("pricing.displayPrice", "pricing.price", "pricing.memberOnlyPrice"):
        value = product.get(field, "").strip()
        if value:
            return value
    return "N/A"


def get_product_image(product_id: str) -> Optional[str]:
    """Get product image as base64"""
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        image_path = IMAGES_DIR / f"{product_id}{ext}"
        if image_path.exists():
            try:
                with open(image_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                print(f"Failed to read image {image_path}: {e}")
                continue
    return None


def search_grocery_items(main_item: str, full_title: str) -> list[dict]:
    """Search for top 3 matching grocery items"""
    products = load_products()

    if not products:
        return []

    full_title_norm = normalize_text(full_title)
    main_item_norm = normalize_text(main_item)

    # Filter by main item
    candidates = [
        p for p in products
        if main_item_norm in normalize_text(p.get("title", ""))
    ]

    if not candidates:
        candidates = products

    # Score and filter
    results = []
    for product in candidates:
        title = product.get("title", "Unknown")
        score = calculate_similarity(full_title, title)

        if score >= 40 or main_item_norm in normalize_text(title):
            results.append({
                "score": score,
                "product": product,
                "product_id": product.get("productId", "unknown"),
            })

    # Sort by score and get top 3
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]


# Routes
@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "Grocery Search MCP Server",
        "status": "ready",
        "csv": str(CSV_FILE.exists()),
        "images": str(IMAGES_DIR.exists()),
    }


@app.post("/search")
async def search(request: GrocerySearchRequest) -> SearchResponse:
    """
    Search for grocery items

    Args:
        main_item: Main category (e.g., "chicken")
        full_title: Full product description (e.g., "organic local chicken breast")

    Returns:
        Top 3 matching items with scores 0-100
    """
    results_raw = search_grocery_items(request.main_item, request.full_title)

    results = []
    for item in results_raw:
        product = item["product"]
        product_id = item["product_id"]

        result_item = GroceryItem(
            title=product.get("title", "Unknown"),
            similarity_score=item["score"],
            product_id=product_id,
            brand=product.get("brand", ""),
            description=product.get("description", ""),
            package_sizing=product.get("packageSizing", ""),
            price_current=format_price(product),
            price_original=product.get("pricing.wasPrice", ""),
            deal_text=product.get("deal.text", ""),
            inventory=product.get("inventoryIndicator.text", ""),
            image_base64=get_product_image(product_id),
            product_link=product.get("link", ""),
        )
        results.append(result_item)

    return SearchResponse(
        results=results,
        query_main=request.main_item,
        query_full=request.full_title,
    )


@app.options("/{path:path}", tags=["CORS"])
async def options_handler(path: str, request: Request):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )


if __name__ == "__main__":
    import uvicorn

    print("\n🚀 Starting Grocery Search MCP Server")
    print(f"📍 URL: http://localhost:8000")
    print(f"📂 CSV: {CSV_FILE} (exists: {CSV_FILE.exists()})")
    print(f"🎞️  Images: {IMAGES_DIR} (exists: {IMAGES_DIR.exists()})")
    print("\n✓ CORS enabled for MCP Inspector (browser-based)")
    print("🔗 POST /search to search for items")
    print("📊 GET / for health check\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
