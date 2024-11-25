
# API Endpoints Documentation


## API Version Status

| Service | Endpoint Group | Version | Status | Notes |
|---------|---------------|---------|---------|-------|
| Producer | Core Endpoints (`/`, `/status`, `/metrics`) | v1.0 | Production | Stable, fully tested |
| Producer | Control Endpoints (`/start`, `/stop`) | v1.0 | Production | Stable, fully tested |
| Producer | Manual Controls (`/fetch`, `/config`) | v0.9 | Beta | Rate limiting being fine-tuned |
| Consumer | Core Endpoints (`/`, `/status`, `/metrics`) | v1.0 | Production | Stable, fully tested |
| Consumer | Control Endpoints (`/start`, `/stop`) | v1.0 | Production | Stable, fully tested |

> **Note**: The API is currently under active development. While production endpoints are stable and fully tested, beta endpoints may undergo changes in future releases. Please check the documentation regularly for updates.

## Upcoming Features
- WebSocket endpoints for real-time metrics (Planned)
- Enhanced rate limiting controls (Beta)
- Batch processing endpoints (Planned)
- Advanced configuration endpoints (Planned)


## Version Change Log

### v1.0 (Current Production)
- Stable core endpoints
- Basic metrics and monitoring
- Service control endpoints

### v0.9 (Current Beta)
- Manual fetch controls
- Configuration management
- Enhanced rate limiting

### Planned (Future)
- WebSocket support
- Advanced metrics
- Batch operations
- Custom roast style configuration

## Production vs Beta Endpoints

### Production Endpoints
Production endpoints are:
- Fully tested
- Stable interfaces
- Backwards compatible
- Production-ready error handling
- Comprehensive monitoring

### Beta Endpoints
Beta endpoints are:
- Under active development
- May have interface changes
- Limited error handling
- Basic monitoring
- Subject to rate limit adjustments

> **Important**: While beta endpoints are functional, they should be used with caution in production environments. Consider implementing fallback mechanisms when using beta endpoints.



This document details all available API endpoints for both the Producer and Consumer services of the Twitter Roaster Bot.

## Producer Service (Default Port: 8000)

### Health Check
```http
GET /
```
Returns the service status.

**Response**
```json
{
    "message": "Welcome to the Twitter Mentions Producer Service!",
    "status": "running"
}
```

### Get Producer Status
```http
GET /status
```
Returns detailed status of the producer service.

**Response**
```json
{
    "is_running": true,
    "last_fetch_time": "2024-11-25T10:30:00.000Z",
    "fetch_interval": 60,
    "processed_count": 42,
    "error_count": 0
}
```

### Start Producer
```http
POST /start
```
Starts the Twitter mention monitoring service.

**Response**
```json
{
    "message": "Producer started successfully"
}
```

**Error Response** (If already running)
```json
{
    "message": "Producer is already running"
}
```

### Stop Producer
```http
POST /stop
```
Stops the Twitter mention monitoring service.

**Response**
```json
{
    "message": "Producer stopped successfully"
}
```

**Error Response** (If not running)
```json
{
    "message": "Producer is not running"
}
```

### Manual Fetch
```http
POST /fetch
```
Manually triggers a Twitter mentions fetch.

**Response**
```json
{
    "message": "Found and processing 5 mentions"
}
```

**Error Response** (Rate limited)
```json
{
    "error": "Rate limit reached. Please try again later."
}
```

### Get Metrics
```http
GET /metrics
```
Returns service metrics and statistics.

**Response**
```json
{
    "processed_mentions": 42,
    "errors": 0,
    "uptime": "Running",
    "last_fetch": "2024-11-25T10:30:00.000Z",
    "fetch_interval_seconds": 60,
    "kafka_topic": "twitter.mentions",
    "twitter_username": "YourBotUsername"
}
```

### Update Configuration
```http
PUT /config
```
Updates the mention fetch interval.

**Parameters**
- `new_interval`: Integer (seconds, minimum 60)

**Request**
```http
PUT /config?new_interval=120
```

**Response**
```json
{
    "message": "Fetch interval updated to 120 seconds"
}
```

**Error Response** (Invalid interval)
```json
{
    "error": "Interval must be at least 60 seconds"
}
```

## Consumer Service (Default Port: 8001)

### Health Check
```http
GET /
```
Returns the service status.

**Response**
```json
{
    "message": "Twitter Roaster Consumer Service"
}
```

### Get Consumer Status
```http
GET /status
```
Returns detailed status of the consumer service.

**Response**
```json
{
    "is_running": true,
    "processed_count": 35,
    "error_count": 0
}
```

### Start Consumer
```http
POST /start
```
Starts the roast generation consumer service.

**Response**
```json
{
    "message": "Consumer started successfully"
}
```

**Error Response** (If already running)
```json
{
    "message": "Consumer is already running"
}
```

### Stop Consumer
```http
POST /stop
```
Stops the roast generation consumer service.

**Response**
```json
{
    "message": "Consumer stopped successfully"
}
```

**Error Response** (If not running)
```json
{
    "message": "Consumer is not running"
}
```

### Get Metrics
```http
GET /metrics
```
Returns service metrics and statistics.

**Response**
```json
{
    "processed_mentions": 35,
    "errors": 0,
    "uptime": "Running",
    "kafka_topic": "twitter.mentions",
    "roast_style": "savage"
}
```

## Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

## Rate Limiting

- Producer Service: Manual fetch is limited to once per minute
- Consumer Service: Twitter API rate limits apply for posting responses

## Error Handling

All endpoints return error responses in the following format:
```json
{
    "error": "Error message description"
}
```

## Monitoring Best Practices

1. Health Monitoring:
   - Regularly poll the `/` endpoint of both services
   - Monitor the `is_running` status via `/status` endpoint

2. Performance Monitoring:
   - Track metrics via `/metrics` endpoint
   - Monitor error counts and processing counts
   - Watch for increasing error rates

3. Rate Limit Monitoring:
   - Check producer metrics for Twitter API rate limit info
   - Monitor consumer error counts for rate limit violations

## Examples

### cURL Examples

1. Start Producer:
```bash
curl -X POST http://localhost:8000/start
```

2. Check Consumer Status:
```bash
curl http://localhost:8001/status
```

3. Update Fetch Interval:
```bash
curl -X PUT "http://localhost:8000/config?new_interval=120"
```

### Python Examples

```python
import requests

# Check producer metrics
response = requests.get('http://localhost:8000/metrics')
metrics = response.json()
print(f"Processed mentions: {metrics['processed_mentions']}")

# Start consumer
response = requests.post('http://localhost:8001/start')
if response.status_code == 200:
    print("Consumer started successfully")
```

## WebSocket Endpoints (Future Implementation)

Future versions may include WebSocket endpoints for real-time monitoring:
```
ws://localhost:8000/ws/metrics
ws://localhost:8001/ws/metrics
```

These endpoints would provide real-time updates of service metrics and status changes.