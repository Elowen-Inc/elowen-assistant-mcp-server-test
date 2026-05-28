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
    cmd = message.strip().split()[0].lower() if message.strip() else ""

    if cmd == "/productcard":
        return _fixture_product_card()
    if cmd == "/productcards":
        return _fixture_product_cards()
    if cmd == "/confirmationmessage":
        return _fixture_confirmation()
    if cmd == "/errormessage":
        return _fixture_error()

    return QueryResponse(
        type="message",
        text=f"[Dev echo] You asked: {message}",
        products=[],
    )


# ── Dev fixtures ──────────────────────────────────────────────────────────────

def _fixture_product_card() -> QueryResponse:
    return QueryResponse(
        type="message",
        text="Here's a product I found for you.",
        products=[
            ProductResponse(
                brand="Organic Valley",
                title="Whole Milk",
                price="$6.49",
                meta="1 gallon (3.78 L)",
                highlight="⭐ Top Rated",
                description="Certified organic whole milk from pasture-raised cows. Rich flavour, no added hormones.",
                imageBase64=None,
                bannerText="Organic",
                bannerColor="#22C55E",
            )
        ],
    )


def _fixture_product_cards() -> QueryResponse:
    return QueryResponse(
        type="message",
        text="Here are a few options that match your request.",
        products=[
            ProductResponse(
                brand="Organic Valley",
                title="Whole Milk",
                price="$6.49",
                meta="1 gallon (3.78 L)",
                highlight="⭐ Top Rated",
                description="Certified organic whole milk from pasture-raised cows.",
                imageBase64=None,
                bannerText="Organic",
                bannerColor="#22C55E",
            ),
            ProductResponse(
                brand="Natrel",
                title="2% Partly Skimmed Milk",
                price="$4.99",
                meta="2 L",
                highlight=None,
                description="Smooth and light with 2% fat. A Canadian household staple.",
                imageBase64=None,
                bannerText="On Sale",
                bannerColor="#F59E0B",
            ),
            ProductResponse(
                brand="Lactantia",
                title="Lactose-Free Whole Milk",
                price="$5.79",
                meta="1 L",
                highlight="Lactose-free",
                description="All the nutrition of whole milk without the lactose.",
                imageBase64=None,
                bannerText=None,
                bannerColor=None,
            ),
        ],
    )


def _fixture_confirmation() -> QueryResponse:
    return QueryResponse(
        type="confirmation",
        question="Which type of milk would you prefer?",
        choices=[
            ChoiceResponse(label="Whole milk",       icon="drop.fill",      type="primary"),
            ChoiceResponse(label="2% or skim",       icon="drop",           type="secondary"),
            ChoiceResponse(label="Skip for now",     icon="xmark",          type="skip"),
        ],
    )


def _fixture_error() -> QueryResponse:
    return QueryResponse(
        type="error",
        message="Sorry, I wasn't able to find any matching products in the catalogue right now. Please try again in a moment.",
    )


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
        )
