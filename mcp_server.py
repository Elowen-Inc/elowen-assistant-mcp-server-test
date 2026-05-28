from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional
import base64

mcp = FastMCP("Elowen Orchestrator")


# ── Response models ───────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    brand:       str
    title:       str
    price:       str
    meta:        Optional[str] = None
    highlight:   Optional[str] = None
    description: str
    imageBase64: Optional[str] = None
    bannerText:  Optional[str] = None
    bannerColor: Optional[str] = None


class ChoiceResponse(BaseModel):
    label: str
    icon:  Optional[str] = None  # SF Symbol name
    type:  str                   # "primary" | "secondary" | "skip"


class QueryResponse(BaseModel):
    type:     str                                  # "message" | "confirmation" | "error"
    text:     Optional[str]                  = None
    products: Optional[list[ProductResponse]] = None
    question: Optional[str]                  = None
    choices:  Optional[list[ChoiceResponse]]  = None
    message:  Optional[str]                  = None


# ── Tool ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def query(
    session_id:       str,
    message:          str,
    skill_level:      Optional[str] = None,
    home_type:        Optional[str] = None,
    budget:           Optional[str] = None,
    complexity_level: Optional[str] = None,
    local_climate:    Optional[str] = None,
    image:            Optional[str] = None,  # base64 JPEG
) -> QueryResponse:
    """
    Route a sanitized user message to the appropriate agent and return a typed response.

    The message has already been PII-sanitized on-device. Personal identifiers
    are replaced with typed placeholders: [name], [address], [postal-code], [phone], [email].
    """
    context = {k: v for k, v in {
        "skill_level":      skill_level,
        "home_type":        home_type,
        "budget":           budget,
        "complexity_level": complexity_level,
        "local_climate":    local_climate,
    }.items() if v is not None}

    image_bytes = base64.b64decode(image) if image else None

    try:
        return orchestrate(
            session_id=session_id,
            message=message,
            context=context,
            image=image_bytes,
        )
    except Exception as e:
        return QueryResponse(type="error", message=str(e))


def orchestrate(
    session_id: str,
    message:    str,
    context:    dict,
    image:      Optional[bytes],
) -> QueryResponse:
    """Stub — replace with real agent routing."""
    return QueryResponse(
        type="message",
        text=f"[Dev echo] You asked: {message}",
        products=[],
    )


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8080
        )
