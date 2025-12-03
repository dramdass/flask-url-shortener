# Flask URL Shortener

A simple URL shortener API built with Flask. Great for learning, demos, or as a starting point for adding features.

## Features

- **Create short URLs** - POST to `/shorten` with a long URL
- **Redirect** - GET `/<short_code>` redirects to the original URL
- **Statistics** - GET `/stats/<short_code>` shows click counts
- **Health check** - GET `/health` returns service status

## Quick Start

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the server
python app.py
```

Server runs on `http://localhost:5000`

## API Usage

### Create a shortened URL
```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "user_id": "alice"}'
```

Response:
```json
{
  "short_url": "http://short.url/a1b2c3d4",
  "long_url": "https://example.com"
}
```

### Use the shortened URL
```bash
curl http://localhost:5000/a1b2c3d4?user_id=alice
# Redirects to https://example.com
```

### Get statistics
```bash
curl http://localhost:5000/stats/a1b2c3d4
```

Response:
```json
{
  "short_code": "a1b2c3d4",
  "long_url": "https://example.com",
  "clicks": 42
}
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorten` | Create a shortened URL |
| GET | `/<short_code>` | Redirect to original URL |
| GET | `/stats/<short_code>` | View click statistics |
| GET | `/health` | Health check |

## Parameters

- `url` (required) - The long URL to shorten
- `user_id` (optional) - User identifier, defaults to "anonymous"

## Notes

**This is a demo application:**
- Uses in-memory storage (data lost on restart)
- No authentication
- No rate limiting (see below)
- Not production-ready

## Want to Add Features?

This app is intentionally simple and missing common features like:
- Rate limiting
- Persistent storage (database)
- Authentication
- Custom short codes
- URL validation
- Analytics

Perfect for learning or experimenting with adding new functionality!

### Example: Adding Rate Limiting

Want to see how to add rate limiting to this app using AI agents? Check out the [AgentFleet URL Shortener Example](https://github.com/dramdass/agentfleet/tree/master/examples/url-shortener-rate-limiting).

## License

MIT
