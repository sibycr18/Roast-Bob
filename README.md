
# Roast_Bob: Twitter Roaster Bot

A scalable Twitter agent service that automatically generates witty roasts in response to mentions using Together AI's LLaMA model. The service uses a microservices architecture with Kafka for message queuing, Redis for caching, and FastAPI for API endpoints.

## 🌟 Features

- Real-time monitoring of Twitter mentions
- AI-powered roast generation using Together AI's LLaMA model
- Scalable microservices architecture
- Rate limiting and caching with Redis
- Kafka-based message queue for reliable processing
- RESTful APIs for monitoring and control
- Docker support for easy deployment

## 🏗️ Architecture

The service consists of two main components:
1. **Producer Service**: Monitors Twitter for mentions and publishes them to Kafka
2. **Consumer Service**: Processes mentions from Kafka and generates roasts using Together AI

For detailed architecture information, see [Architecture Documentation](docs/ARCHITECTURE.md)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Twitter Developer Account with API credentials
- Together AI API key

### Environment Variables

Create a `.env` file with the following variables:

```env
TOGETHER_API_KEY=your_together_ai_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN_CONSUMER=your_bearer_token_for_consumer
TWITTER_BEARER_TOKEN_PRODUCER=your_bearer_token_for_producer
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Roast-Bob.git
cd Roast-Bob
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

For detailed setup instructions, see [Setup Documentation](docs/setup.md)

## 🎮 Usage

1. Start the infrastructure services:
```bash
docker-compose up -d
```

2. Start the producer service:
```bash
uvicorn producer:app --reload --port 8000
```

3. Start the consumer service:
```bash
uvicorn consumer:app --reload --port 8001
```
*Note: All of the above should be run in seperate terminals*


## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
