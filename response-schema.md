# Response Schema

This file defines the structure of every response type the orchestrator can return and the iOS component each one maps to. The orchestrator decides *which* type to return; this document defines *what that type must contain* and *what the app renders*.

Every response has a `type` field. The app reads `type` first and routes accordingly.

---

## type: `"message"`

**Renders as:** `ElowenChatBubble` for the text, followed by zero or more `ProductCard`s inline below it.

```json
{
  "type": "message",
  "text": "string (required)",
  "products": [ ProductObject ]   // optional — omit or empty array for text-only
}
```

### Product object

```json
{
  "brand":       "string (required)  — store or manufacturer label",
  "title":       "string (required)  — full product name",
  "price":       "string (required)  — formatted, e.g. \"$18.99\"",
  "meta":        "string | null      — size, unit, quantity e.g. \"946 mL\"",
  "highlight":   "string | null      — short tag shown below price e.g. \"⭐ Top Rated\"",
  "description": "string (required)  — one or two sentences",
  "imageBase64": "string | null      — raw base64 of a product image",
  "bannerText":  "string | null      — if present, a coloured strip appears at the top of the card",
  "bannerColor": "string | null      — hex colour for the banner e.g. \"#22C55E\" (required when bannerText is set)"
}
```

### Rendering rules

| `products` value | What renders |
|---|---|
| Absent or empty `[]` | Single `ElowenChatBubble` — text only |
| 1–3 items | `ElowenChatBubble` + one `ProductCard` per item, stacked below |

Each `ProductCard` exposes three actions:
- **Add to List** (primary) — persists the product to the user's list
- **Replace** (secondary) — app sends a follow-up query to find an alternative
- **Skip** (skip) — collapses the card

---

## type: `"confirmation"`

**Renders as:** `ToolPrompt` — an `ElowenChatBubble` with the question text, followed by 2–3 inline choice buttons.

```json
{
  "type":     "confirmation",
  "question": "string (required) — the clarifying question shown in the bubble",
  "choices":  [ ChoiceObject ]   // required — 2 or 3 items, avoid 4+
}
```

### Choice object

```json
{
  "label": "string (required) — button label shown to the user",
  "icon":  "string | null    — SF Symbol name e.g. \"checkmark\", \"xmark\", \"arrow.clockwise\"",
  "type":  "\"primary\" | \"secondary\" | \"skip\""
}
```

### Choice type → button variant → tap behaviour

| `type` | Button colour | What happens when tapped |
|---|---|---|
| `"primary"` | Blue | App sends a follow-up query with the choice `label` as the message |
| `"secondary"` | Amber | Button enters picked state; input bar is focused so user can type a correction |
| `"skip"` | Red | `ToolPrompt` collapses; no request is sent |

Convention: the last choice in the array is typically `"skip"` so the user can always dismiss.

---

## type: `"error"`

**Renders as:** `ElowenChatBubble` with the error text, inline in the chat stream. No modal, no alert.

```json
{
  "type":    "error",
  "message": "string (required) — shown directly in the chat bubble"
}
```

Use this for application-level failures where the server received and understood the request but cannot produce a response (e.g. agent timeout, no catalog match that requires explanation, safety deferral). Transport-level failures (network unreachable, HTTP 5xx) are handled independently by the iOS client and never reach this path.

---

## Summary table

| `type` | iOS component | Required fields | Optional fields |
|---|---|---|---|
| `"message"` | `ElowenChatBubble` + `ProductCard`(s) | `text` | `products[]` |
| `"confirmation"` | `ToolPrompt` | `question`, `choices[]` | — |
| `"error"` | `ElowenChatBubble` | `message` | — |

## References

`response-handling.md`, `ui-elements.md`, `../backend/orchestrator.md`, `../../MCP_SERVER.md`
