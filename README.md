# Grocery Search MCP Server

A FastAPI-based MCP (Model Context Protocol) server that searches for grocery items by similarity and returns the top 3 matches with product information and images.

## 🎯 Features

- **Similarity Scoring**: Matches items with scores from 0-100 (100 = exact match)
- **Image Support**: Returns product images as base64-encoded data
- **Rich Results**: Includes price, brand, package sizing, deals, stock info
- **CORS Enabled**: Works with browser-based MCP Inspector
- **HTTP Stream**: FastAPI with proper async support

## 🐛 CORS Issue Fixed

**Problem**: MCP Inspector (browser-based) sends OPTIONS preflight requests → `405 Method Not Allowed`

**Solution**:
1. Add CORS middleware **FIRST** (before routes)
2. Allow all HTTP methods including OPTIONS
3. Explicit OPTIONS endpoint handler

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # ✓ Includes OPTIONS
    allow_headers=["*"],
)
```

## 📋 Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- See `requirements-mcp.txt`

## 🚀 Quick Start

### 1. Install
```bash
bash setup.sh
```

Or manually:
```bash
pip install -r requirements-mcp.txt
```

### 2. Run Server
```bash
python mcp_server.py
```

Output:
```
🚀 Starting Grocery Search MCP Server
📍 URL: http://localhost:8000
✓ CORS enabled for MCP Inspector (browser-based)
```

### 3. Test Endpoint
```bash
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "main_item": "chicken",
    "full_title": "organic local chicken breast"
  }'
```

Or use the test client:
```bash
python test_client.py
```

## 📡 API Endpoints

### POST /search
Search for grocery items

**Request**:
```json
{
  "main_item": "chicken",
  "full_title": "organic local chicken breast"
}
```

**Response**:
```json
{
  "results": [
    {
      "title": "Chicken Breast Organic",
      "similarity_score": 95,
      "product_id": "20091825001_EA",
      "brand": "Brand Name",
      "description": "...",
      "package_sizing": "1kg",
      "price_current": "$9.99",
      "price_original": "$12.99",
      "deal_text": "Save 25%",
      "inventory": "In Stock",
      "image_base64": "iVBORw0KGGoAAAANSUhEUgAAAA...",
      "product_link": "https://..."
    },
    ...
  ],
  "query_main": "chicken",
  "query_full": "organic local chicken breast"
}
```

### GET /
Health check

**Response**:
```json
{
  "name": "Grocery Search MCP Server",
  "status": "ready",
  "csv": "true",
  "images": "true"
}
```

## 📊 Data Source

- **CSV**: `grocery_data_feb_2025_ref.csv` (~45 columns)
- **Images**: `product_images/` folder
  - Files named: `{productId}.{ext}` (e.g., `20091825001_EA.png`)
  - Supported: .png, .jpg, .jpeg, .webp

## 🔍 Similarity Scoring

Uses Python's `difflib.SequenceMatcher`:
- **100**: Exact match
- **80-99**: Highly similar
- **60-79**: Very similar
- **40-59**: Similar
- **<40**: Filtered out

Results filtered for `main_item` presence in title, then top 3 returned.

## 🛠️ Development

### Project Structure
```
grocery_search/
├── mcp_server.py              # Main MCP server
├── test_client.py             # Test client
├── setup.sh                   # Setup script
├── requirements-mcp.txt       # Dependencies
├── grocery_data_feb_2025_ref.csv
├── product_images/            # Product image folder
├── search_ref.py              # Original CLI search tool
└── venv/
```

### Testing
```bash
python test_client.py
```

## 🔗 Integration

### Python Client
```python
import httpx

response = httpx.post(
    "http://localhost:8000/search",
    json={"main_item": "chicken", "full_title": "chicken breast"}
)

results = response.json()
for item in results["results"]:
    print(f"{item['title']} - {item['similarity_score']}% match")
```

### MCP Inspector (Browser)
1. Open MCP Inspector
2. Connect to `http://localhost:8000`
3. Call `/search` tool
4. Images load directly in UI

## 📝 Notes

- Server caches CSV in memory on first load
- Images converted to base64 (efficient for JSON)
- All fields from CSV available in product dict
- Supports streaming responses for large image data

## 🐛 Troubleshooting

### "Cannot connect to server"
- Check server is running: `python mcp_server.py`
- Verify port 8000 is available: `lsof -i :8000`

### "405 Method Not Allowed"
- CORS middleware was added before this fix
- Verify `mcp_server.py` has the updated code

### "Image not found"
- Check `product_images/` folder exists
- Verify image files match product IDs
- Check file extensions (.png, .jpg, etc.)

### "CSV not found"
- Place `grocery_data_feb_2025_ref.csv` in same directory as `mcp_server.py`
- Path: `/home/behnam/grocery_search/grocery_data_feb_2025_ref.csv`

## 📄 License

Internal project
