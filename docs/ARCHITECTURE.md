
# Architecture Documentation

## System Overview

The Twitter Roaster Bot is built using a microservices architecture pattern, separating the concerns of mention monitoring and roast generation into distinct services. This design allows for better scalability, maintainability, and reliability.

## Components

### 1. Producer Service (producer.py)

The Producer Service is responsible for:
- Monitoring Twitter for new mentions of the bot
- Caching the last processed mention ID in Redis
- Publishing mentions to a Kafka topic
- Rate limiting and error handling
- Providing REST APIs for control and monitoring

Key Features:
- Uses Twitter API v2 via Tweepy
- Implements configurable polling interval
- Provides manual fetch trigger
- Maintains metrics and status information

### 2. Consumer Service (consumer.py)

The Consumer Service handles:
- Consuming mentions from Kafka
- Generating roasts using Together AI
- Posting replies on Twitter
- Managing consumer group offsets
- Providing REST APIs for control and monitoring

Key Features:
- Uses Together AI's LLaMA model for roast generation
- Implements background processing
- Handles Twitter API rate limits
- Maintains processing metrics

### 3. Infrastructure Components

#### Kafka
- Message broker for reliable mention queue
- Enables decoupling of producer and consumer
- Provides message persistence
- Handles consumer group management

#### Redis
- Caches last processed mention ID
- Implements rate limiting
- Provides fast access to frequently used data

#### Docker
- Containerizes infrastructure components
- Enables easy deployment and scaling
- Manages service dependencies

## Data Flow

1. Producer Service:
   ```
   Twitter API → Producer → Kafka Topic
   ```

2. Consumer Service:
   ```
   Kafka Topic → Consumer → Together AI → Twitter API
   ```

## Message Format

Mentions are published to Kafka in the following JSON format:
```json
{
    "id": "tweet_id",
    "text": "tweet_text",
    "author_id": "author_id",
    "conversation_id": "conversation_id",
    "created_at": "iso_timestamp",
    "processed_at": "iso_timestamp",
    "referenced_tweet_id": "referenced_tweet_id"
}
```

## Scalability

The system can be scaled in several ways:
1. Multiple producer instances for higher Twitter API quota utilization
2. Multiple consumer instances for parallel roast generation
3. Kafka partitioning for distributed processing
4. Redis clustering for improved caching performance

## Error Handling

The system implements several error handling mechanisms:
- Automatic retries for failed API calls
- Dead letter queues for failed messages
- Error logging and metrics
- Rate limit handling and backoff

## Monitoring

Both services expose metrics endpoints that provide:
- Processing counts
- Error counts
- Service status
- Processing latency
- Rate limit information

## Security Considerations

- API keys and secrets are managed via environment variables
- Network security is handled via Docker network isolation
- Rate limiting prevents abuse
- Error logging excludes sensitive information