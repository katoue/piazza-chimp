# Piazza-Chimp

An intelligent bot that automatically generates and posts AI-powered answers to student questions on Piazza using Claude.

## Overview

Piazza-Chimp is a polling bot that monitors Piazza forums, intelligently identifies answerable questions, and uses the Anthropic Claude API to generate high-quality responses. The bot respects instructor authority by only answering questions that lack instructor answers and aren't marked for instructor review.

## Features

- **Autonomous Monitoring**: Continuously polls Piazza for unanswered student questions
- **Intelligent Filtering**: Respects course policies by skipping questions with instructor answers or special tags
- **AI-Generated Responses**: Leverages Claude API to generate contextually appropriate answers
- **RAG Integration**: Incorporates course materials and Q&A history via vector embeddings for more contextually accurate responses
- **Persistent Tracking**: Uses SQLite to track answered questions and avoid duplicate responses
- **Error Resilience**: Graceful fallback mechanisms and comprehensive logging
- **Flexible Posting**: Attempts instructor answers first, falls back to student followups with proper attribution
- **Rate Limiting**: Configurable delays to respect API quotas and platform limits

## Prerequisites

- Python 3.8+
- Piazza account with course access
- Anthropic API key
- `.env` file with required credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/piazza-chimp.git
cd piazza-chimp
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Piazza Credentials
PIAZZA_EMAIL=your-email@example.com
PIAZZA_PASSWORD=your-piazza-password
PIAZZA_NETWORK=your-course-network-id

# Course Information
COURSE_NAME=CS 101

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional: Discord Webhook (for notifications)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Configuration File

Additional settings are available in `config.py`:

- `POLL_INTERVAL_SEC`: How often to check for new questions (default: 300 seconds)
- `PIAZZA_CALL_SLEEP`: Delay between API calls (default: 2 seconds)
- `DB_PATH`: Location of the SQLite database (default: `piazza_chimp.db`)
- `AI_DISCLAIMER`: Disclaimer text appended to all generated answers

## RAG (Retrieval Augmented Generation) Setup

The bot can use course materials and Piazza Q&A history to provide more contextually accurate answers.

### Ingest Course Materials

To ingest course materials (PDFs, Markdown, plain text) into the vector database:

```bash
python ingest_materials.py --dir ./course_files [--ext pdf,md,txt]
```

### Ingest Piazza Q&A History

To ingest historical Q&A from Piazza:

```bash
python ingest_piazza.py
```

This ingests all posts with accepted answers from your course, which the bot can then reference when generating new answers.

## Usage

Start the bot:

```bash
python bot.py
```

The bot will:
1. Log in to Piazza
2. Begin polling for unread questions
3. Generate answers for eligible questions
4. Post answers and track them in the database
5. Continue monitoring until interrupted (Ctrl+C)

### Logging

All activity is logged to console. Monitor the logs to verify the bot is functioning correctly and to debug any issues.

## Architecture

### Core Components

- **bot.py**: Main polling loop and orchestration
- **piazza_client.py**: Piazza API wrapper with filtering logic
- **ai_answerer.py**: Claude API integration for answer generation
- **db.py**: SQLite database management
- **config.py**: Application configuration constants

### Answer Filtering

The bot only answers questions that meet ALL of these criteria:

1. **Type**: Must be a question (not a note)
2. **No Instructor Answer**: Post must not already have an instructor answer
3. **No Instructor Note Tag**: Post must not be tagged "instructor-note"
4. **Not Previously Answered**: Bot tracks answered posts in the database

### Answer Posting Strategy

1. **Attempt 1**: Post as instructor answer (if permitted)
2. **Fallback**: Post as student followup with "AI Bot - Generated Answer" prefix
3. **Tracking**: Record in database to avoid duplicate answers

## Development

### Project Structure

```
piazza-chimp/
├── bot.py                 # Main bot loop
├── piazza_client.py      # Piazza API wrapper
├── ai_answerer.py        # Claude integration
├── db.py                 # Database management
├── config.py             # Configuration
├── ingest_piazza.py      # Ingest Q&A history into RAG
├── ingest_materials.py   # Ingest course materials into RAG
├── rag/                  # RAG module
│   ├── vector_store.py   # ChromaDB integration
│   └── ingester.py       # Document ingestion utilities
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── piazza_chimp.db       # SQLite database (auto-created)
├── chroma_db/            # Vector database (auto-created)
└── README.md             # This file
```

### Dependencies

- **piazza-api**: Piazza platform integration
- **anthropic**: Claude API client
- **python-dotenv**: Environment variable management
- **chroma-client**: Vector database for RAG
- **pypdf**: PDF document processing
- **markdown**: Markdown document processing
- **discord-webhook**: Optional Discord notifications

## Best Practices

1. **Testing**: Start with a test course to validate configuration
2. **Monitoring**: Regularly check logs to ensure the bot is functioning
3. **Rate Limits**: Adjust `POLL_INTERVAL_SEC` and `PIAZZA_CALL_SLEEP` based on API quotas
4. **Backups**: Periodically backup `piazza_chimp.db` to preserve answer history
5. **Credentials**: Never commit `.env` or `secrets.py` files to version control

## Troubleshooting

### Bot won't start

- Verify Piazza credentials in `.env`
- Ensure Anthropic API key is valid
- Check that all dependencies are installed

### No answers being posted

- Check logs for filtering reasons (instructor answer exists, instructor-note tag, etc.)
- Verify ANTHROPIC_API_KEY is valid
- Ensure course access on Piazza

### Rate limit errors

- Increase `PIAZZA_CALL_SLEEP` in `config.py`
- Increase `POLL_INTERVAL_SEC` to reduce polling frequency
- Check Anthropic API usage in console

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is designed for educational use. Ensure that using automated answers complies with your course's academic integrity policies and Piazza's terms of service. Always include proper attribution for AI-generated content.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
