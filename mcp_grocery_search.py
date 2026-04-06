from fastmcp import FastMCP
from datetime import datetime
import search_ref
import base64
import os
import mimetypes

mcp = FastMCP("RPi-Echo-Test")


@mcp.tool()
def ping(message: str = "ping") -> dict:
    """
    Responds with a simple 'pong' structure.
    Useful for client initialization and connectivity checks.
    """
    return {
        "ok": True,
        "echo": message,
        "reply": "pong",
        "server": "raspberry-pi",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def _encode_image(image_path: str) -> tuple[str, str]:
    if not os.path.exists(image_path):
        return "", ""
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"  # fallback
        
    try:
        try:
            from PIL import Image
            import io
            with Image.open(image_path) as img:
                # Resize to keep payload reasonable
                img.thumbnail((400, 400))
                buffer = io.BytesIO()
                # Use format based on mime_type
                save_format = "PNG" if mime_type == "image/png" else "JPEG"
                if save_format == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffer, format=save_format, optimize=True, quality=85)
                img_bytes = buffer.getvalue()
        except ImportError:
            # Fallback if Pillow is not installed
            with open(image_path, "rb") as f:
                img_bytes = f.read()
                
        return base64.b64encode(img_bytes).decode('utf-8'), mime_type
    except Exception as e:
        print(f"Failed to encode {image_path}: {e}")
        return "", ""


@mcp.tool()
def search_grocery(main_item: str, full_title: str) -> dict:
    """
    Searches for grocery products based on main item and full title, returning the top 3 most relevant results with productID, Price, and base64 image data.
    """
    products = search_ref.load_products(search_ref.CSV_FILE)
    best, suggestions = search_ref.find_best_match(full_title, products)
    
    candidates = []
    if best:
        candidates.append(best)
    candidates.extend(suggestions[:2])  # Take up to 2 more from suggestions
    
    results = []
    for product in candidates[:3]:  # Ensure only top 3
        product_id = product.get('productId', '')
        price = search_ref.format_price(product)
        description = product.get('description', '')
        package_sizing = product.get('packageSizing', '')
        
        # Image handling
        image_filename = f"{product_id}.png"
        image_path = os.path.join("product_images", image_filename)
        
        image_b64, image_mime = _encode_image(image_path)
            
        results.append({
            "productID": product_id,
            "Price": price,
            "description": description,
            "packageSizing": package_sizing,
            "imageBase64": image_b64,
            "imageMimeType": image_mime
        })
    
    return {"results": results}


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
        )
