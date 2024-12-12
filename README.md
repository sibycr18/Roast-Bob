# Bluesky Bot

An intelligent Bluesky bot that analyzes trends, responds to mentions, and generates content using AI. The bot maintains a consistent personality while engaging with users and trending topics.

## Features

- **Trend Analysis**: Monitors and analyzes Bluesky feed content
- **Intelligent Responses**: Generates contextual responses to mentions
- **Content Generation**: Creates regular posts based on trending topics
- **Memory Management**: Stores and retrieves past interactions and opinions
- **Roast Mode**: Special response mode for roast requests
- **Automated Posting**: Configurable posting schedule

## Prerequisites

- Python 3.8+
- Bluesky account
- OpenAI API key
- ChromaDB (for memory storage)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd bluesky-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following:
```env
# Bluesky Credentials
BLUESKY_HANDLE=your_handle
BLUESKY_PASSWORD=your_password

# OpenAI API
OPENAI_API_KEY=your_openai_key

# Bot Configuration
POSTING_INTERVAL_HOURS=4
```

## Project Structure

```
bluesky_bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration and constants
├── clients/
│   ├── __init__.py
│   ├── bluesky_client.py    # Bluesky API client
│   └── openai_client.py     # OpenAI API client
├── services/
│   ├── __init__.py
│   ├── mention_handler.py   # Mention processing
│   ├── trend_analyzer.py    # Feed analysis
│   ├── content_generator.py # Post generation
│   └── memory_service.py    # ChromaDB operations
├── utils/
│   ├── __init__.py
│   └── logger.py           # Logging utility
└── main.py                 # Main bot script
```

## Usage

1. Start the bot:
```bash
python main.py
```

The bot will automatically:
- Monitor the Bluesky feed for trends
- Respond to mentions
- Generate regular posts based on trending topics
- Store and learn from interactions

## Configuration

Key settings in `config/settings.py`:
- `FEED_LIMIT`: Maximum number of feed items to analyze
- `MAX_RESPONSE_LENGTH`: Maximum length for responses (280 characters)
- `GPT_MODEL`: OpenAI model to use
- `POSTING_INTERVAL_HOURS`: Hours between regular posts

## Logging

Logs are stored in the `logs/` directory:
- `main.log`: General bot operation
- `mentions.log`: Mention handling
- `trends.log`: Trend analysis
- `content.log`: Content generation
- `memory.log`: Memory operations

## Error Handling

The bot includes comprehensive error handling:
- API rate limit handling
- Connection error recovery
- Graceful shutdown on interruption
- Service failure logging

## Memory Management

The bot uses ChromaDB to store:
- Analyzed trends
- Past interactions
- Generated content
- Bot opinions and thoughts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using the atproto Python library
- Powered by OpenAI's GPT-3.5
- Uses ChromaDB for memory storage