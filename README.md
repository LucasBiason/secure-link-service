# Secure Link Service 🔐

> A lightweight, pluggable microservice for generating and validating secure, time-limited links with encrypted payloads.

## The Problem We're Solving

When building automation integrations (Telegram bots, WhatsApp automation, N8N workflows), we often need to pass authentication tokens and action data to users through links. The challenge? **We can't just put sensitive data in URLs** - that's a security nightmare.

**Common scenarios:**
- A WhatsApp bot needs to send a user a link to approve a report
- An N8N workflow needs to generate a link for editing a rejected expense
- A Telegram bot needs to create a secure link for accessing a specific resource

**The solution?** Encrypt the data, store it temporarily in Redis, and return a short hash. When the user clicks the link, we decrypt and validate everything server-side.

## Features

✨ **Simple API** - Just two endpoints: generate and validate  
🔒 **Secure by Default** - AES-256-GCM encryption with Fernet  
⏱️ **Time-Limited** - Configurable expiration (default: 1 hour)  
🚀 **Fast** - Redis-backed for sub-millisecond lookups  
🔌 **Pluggable** - Works with any system, no dependencies  
📦 **Lightweight** - Minimal dependencies, FastAPI-based  

## Quick Start

### Installation

```bash
git clone https://github.com/LucasBiason/secure-link-service.git
cd secure-link-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
ENCRYPTION_KEY=your-32-byte-base64-encoded-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
LINK_EXPIRATION_HOURS=1
PORT=8011
```

Generate an encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Running

```bash
uvicorn app.main:app --reload --port 8011
```

## API Usage

### Generate a Secure Link

```bash
curl -X POST "http://localhost:8011/links/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "resource_id": "123e4567-e89b-12d3-a456-426614174000",
      "resource_type": "report",
      "action": "edit"
    }
  }'
```

**Response:**
```json
{
  "short_code": "aB3xY9",
  "expires_at": "2026-01-12T11:00:00Z",
  "created_at": "2026-01-12T10:00:00Z"
}
```

### Validate a Secure Link

```bash
curl -X GET "http://localhost:8011/links/aB3xY9/validate"
```

**Response (valid):**
```json
{
  "valid": true,
  "data": {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "resource_type": "report",
    "action": "edit"
  },
  "token": "YOUR_JWT_TOKEN",
  "encrypted_at": "2026-01-12T10:00:00Z"
}
```

**Response (invalid/expired):**
```json
{
  "valid": false,
  "error": "Link not found or expired"
}
```

## How It Works

1. **Generate**: Client sends JWT token + data → Service encrypts everything → Stores in Redis with TTL → Returns short hash
2. **Validate**: Client sends hash → Service looks up in Redis → Decrypts → Validates → Returns original data

### Security Features

- **Encryption**: AES-256-GCM via Fernet (symmetric encryption)
- **Time-Limited**: Links expire after configured time (default: 1 hour)
- **One-Time Use**: Optional (can be configured)
- **Token Validation**: JWT is validated before encryption
- **Tamper-Proof**: Any modification to the hash invalidates the link

## Use Cases

### 1. WhatsApp Bot Integration

```python
import httpx

async def send_approval_link(user_jwt: str, report_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://secure-link-service:8011/links/generate",
            headers={"Authorization": f"Bearer {user_jwt}"},
            json={
                "data": {
                    "report_id": report_id,
                    "action": "approve"
                }
            }
        )
        link_data = response.json()
        # Send link via WhatsApp: https://yourapp.com/link/{link_data['short_code']}
```

### 2. N8N Workflow

Use the HTTP Request node to call the generate endpoint, then send the link via email/SMS/Telegram.

### 3. Telegram Bot

Same pattern - generate link, send to user, they click and get authenticated automatically.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────┐
│   Client    │─────────▶│ Link Service │─────────▶│  Redis  │
│  (Bot/API)  │  POST   │   (FastAPI)  │  Store  │ (Cache) │
└─────────────┘         └──────────────┘         └─────────┘
                              │
                              │ Encrypt/Decrypt
                              ▼
                        ┌──────────────┐
                        │   Fernet     │
                        │  (AES-256)   │
                        └──────────────┘
```

## Project Structure

```
secure-link-service/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── controllers/            # Business logic
│   ├── routers/                # API endpoints
│   ├── repositories/           # Redis operations
│   ├── schemas/                # Pydantic models
│   └── services/               # Encryption, hashing
├── tests/                      # Unit & integration tests
├── docs/                       # Additional documentation
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Code Quality

```bash
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

## Docker

```bash
docker-compose up -d
```

## License

MIT License - feel free to use this in your projects!

## Contributing

Pull requests welcome! This is a personal project, but I'm happy to accept improvements.

## Author

Built to solve a real problem in production automation workflows. If this helps you, let me know! 🚀
