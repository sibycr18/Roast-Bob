
# Setup Documentation

This guide provides detailed instructions for setting up and running the Twitter Roaster Bot.

## Prerequisites

### Required Software
- Python 3.8 or higher
- Docker Engine 20.10.0 or higher
- Docker Compose 2.0.0 or higher
- Git

### API Credentials

1. Twitter Developer Account:
   - Create a project in the [Twitter Developer Portal](https://developer.x.com/en/portal/dashboard)
   - Generate API keys and tokens
   - Enable OAuth 2.0
   - Add required permissions: Read and Write

2. Together AI Account:
   - Sign up at [Together AI](https://together.ai)
   - Generate an API key

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Roast-Bob.git
cd Roast-Bob
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On MacOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:
```env
# Together AI
TOGETHER_API_KEY=your_together_ai_key

# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
# Contact me for Access Tokens of Roast_Bob_AI twitter handle
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN_CONSUMER=your_bearer_token_for_consumer
TWITTER_BEARER_TOKEN_PRODUCER=your_bearer_token_for_producer

# Username of the account which you are using to see the mentions and reply back
# If this is not provided, the Roast_Bob_AI account will be used as default
USERNAME=your_user_name

# Optional Configuration
KAFKA_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379
ROAST_STYLE=savage
```

> [!IMPORTANT]
> For Buildathon Evaluators: Please contact me through whatsapp or call at +919526038363 or through email 'sibycr18@gmail.com' to obtain the ACCESS KEYS of Roast_Bob_AI twitter handle and generate responses though that account.

> [!TIP]
> TWITTER_BEARER_TOKEN_CONSUMER and TWITTER_BEARER_TOKEN_CONSUMER can be the same. Use separate keys for rate limit concerns.

### 5. Infrastructure Setup

Start Kafka and Redis using Docker Compose:
```bash
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

### 6. Running the Services

1. Start the Producer Service:
```bash
uvicorn producer:app --reload --port 8000
```

2. Start the Consumer Service in another terminal:
```bash
uvicorn consumer:app --reload --port 8001
```

### 7. Verify Installation

1. Check Producer Service:
```bash
curl http://localhost:8000/status
```

2. Check Consumer Service:
```bash
curl http://localhost:8001/status
```

## Configuration Options

### Producer Service

You can configure the mention fetch interval (not recommended with free tier API access):
```bash
curl -X PUT "http://localhost:8000/config?new_interval=120"  # Set to 120 seconds
```

### Consumer Service

Modify the roast style through environment variables:
```env
ROAST_STYLE=shakespeare  # Options: savage, shakespeare, etc.
```

## Troubleshooting

### Common Issues

1. Kafka Connection Issues:
   - Ensure Kafka is running: `docker-compose ps`
   - Check logs: `docker-compose logs kafka`
   - Verify KAFKA_SERVERS in .env

2. Redis Connection Issues:
   - Check Redis status: `docker-compose ps`
   - Verify REDIS_URL in .env
   - Check Redis logs: `docker-compose logs redis`

3. Twitter API Issues:
   - Verify API credentials in .env
   - Check rate limits using /metrics endpoint
   - Ensure proper permissions are enabled

### Logs

Access service logs:
```bash
# Producer logs
uvicorn producer:app --log-level debug

# Consumer logs
uvicorn consumer:app --log-level debug

# Infrastructure logs
docker-compose logs -f
```

## Maintenance

### Backup

1. Redis Data:
```bash
docker-compose exec redis redis-cli SAVE
```

2. Kafka Topics:
```bash
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Cleanup

Remove containers and volumes:
```bash
docker-compose down -v
```

Clean Python cache:
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```
