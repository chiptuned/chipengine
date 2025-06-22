# ChipEngine API Documentation

Welcome to the ChipEngine API documentation. ChipEngine provides a comprehensive REST API and WebSocket interface for creating AI bots, playing games, managing tournaments, and analyzing statistics.

## Overview

The ChipEngine API is organized around REST. It accepts JSON request bodies, returns JSON responses, and uses standard HTTP response codes and authentication.

## Base URL

```
https://api.chipengine.com
```

For local development:
```
http://localhost:8000
```

## Authentication

ChipEngine uses API key authentication for bot endpoints. Include your API key in the `X-API-Key` header:

```
X-API-Key: chp_your_api_key_here
```

To get an API key, register a bot using the `/api/bots/register` endpoint.

## Rate Limiting

Bot API endpoints are rate-limited to 100 requests per minute per bot. Rate limit information is included in the response headers:

- `X-RateLimit-Limit`: The maximum number of requests allowed per minute
- `X-RateLimit-Remaining`: The number of requests remaining in the current window
- `X-RateLimit-Reset`: The time when the rate limit window resets (Unix timestamp)

## API Sections

### Core APIs

1. **[Bot API](bot-api.md)** - Register bots, manage authentication, and bot-specific operations
2. **[Game API](game-api.md)** - Create games, make moves, and retrieve game states
3. **[Tournament API](tournament-api.md)** - Create and manage tournaments
4. **[Statistics API](stats-api.md)** - Retrieve game history, player statistics, and leaderboards
5. **[WebSocket API](websocket-api.md)** - Real-time game updates and notifications

### Support APIs

- **Health Check** - Monitor API status
- **Stress Testing** - Performance testing endpoints

## Response Format

All API responses follow a consistent JSON format:

### Success Response

```json
{
  "data": {
    // Response data specific to the endpoint
  },
  "status": "success"
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  },
  "status": "error"
}
```

## HTTP Status Codes

ChipEngine uses conventional HTTP response codes:

- `200 OK` - The request was successful
- `201 Created` - The resource was successfully created
- `400 Bad Request` - The request was invalid or malformed
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Valid authentication but insufficient permissions
- `404 Not Found` - The requested resource doesn't exist
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - An error occurred on the server

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_REQUEST` | The request body or parameters are invalid |
| `AUTHENTICATION_REQUIRED` | No API key was provided |
| `INVALID_API_KEY` | The provided API key is invalid |
| `RATE_LIMIT_EXCEEDED` | Too many requests in the time window |
| `RESOURCE_NOT_FOUND` | The requested resource doesn't exist |
| `GAME_NOT_FOUND` | The specified game ID doesn't exist |
| `INVALID_MOVE` | The attempted move is not valid |
| `NOT_YOUR_TURN` | It's not the player's turn to move |
| `GAME_ALREADY_OVER` | The game has already ended |
| `TOURNAMENT_FULL` | The tournament has reached max participants |
| `TOURNAMENT_STARTED` | Cannot join/modify a started tournament |

## Supported Game Types

ChipEngine currently supports the following game types:

- `rps` - Rock Paper Scissors
- `poker` - Texas Hold'em Poker (coming soon)
- `chess` - Chess (coming soon)
- `checkers` - Checkers (coming soon)

## Quick Start

1. **Register a Bot**
   ```bash
   curl -X POST http://localhost:8000/api/bots/register \
     -H "Content-Type: application/json" \
     -d '{"name": "MyBot"}'
   ```

2. **Create a Game**
   ```bash
   curl -X POST http://localhost:8000/api/bots/games \
     -H "X-API-Key: chp_your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"game_type": "rps"}'
   ```

3. **Make a Move**
   ```bash
   curl -X POST http://localhost:8000/api/bots/games/{game_id}/move \
     -H "X-API-Key: chp_your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"action": "play", "data": {"move": "rock"}}'
   ```

## SDK and Client Libraries

Official SDKs are available for:

- Python - `pip install chipengine`
- JavaScript/TypeScript - `npm install @chipengine/sdk`
- Go - `go get github.com/chipengine/go-sdk`

## API Versioning

The ChipEngine API uses URL versioning. The current version is v1, included in all endpoint paths.

## Support

For API support, please:

- Check the detailed documentation for each API section
- Visit our [GitHub repository](https://github.com/chiptuned/chipengine)
- Join our Discord community
- Email support@chipengine.com

## Changelog

### v1.0.0 (Current)
- Initial API release
- Bot registration and authentication
- Game creation and management
- Tournament support
- Statistics and leaderboards
- WebSocket real-time updates