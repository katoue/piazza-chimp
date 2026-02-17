# Piazza-Chimp

An intelligent bot that automatically monitors Piazza forums and generates AI-powered answers to student questions using Claude.

## What It Does

Piazza-Chimp polls your Piazza course continuously, identifies unanswered student questions, and uses Claude AI to generate thoughtful, contextually appropriate responses. The bot respects academic policies by:
- Skipping questions that already have instructor answers
- Avoiding questions marked with special tags
- Tracking answered questions to prevent duplicates
- Allowing you to review before answers are posted

## Key Features

- **Automatic Monitoring** - Continuously checks Piazza for new unanswered questions
- **Smart Filtering** - Respects course policies and instructor authority
- **AI-Powered Answers** - Uses Claude to generate high-quality, contextual responses
- **Course Knowledge (RAG)** - Can reference your course materials and past Q&A history for better answers
- **Activity Logging** - Tracks all operations for audit and debugging
- **Error Handling** - Graceful fallbacks if posting fails
- **Configurable** - Easy to customize polling intervals, response style, and more

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file:
```
PIAZZA_EMAIL=your-email@example.com
PIAZZA_PASSWORD=your-password
PIAZZA_NETWORK=your-course-id
COURSE_NAME=Your Course Name
ANTHROPIC_API_KEY=your-api-key
```

### 3. Run

```bash
python bot.py
```

The bot will start monitoring and answering questions automatically.

## Enhance with Course Materials (Optional)

Make answers smarter by adding your course materials to the knowledge base:

### Add Course Files

```bash
# 1. Place PDFs, Markdown, or text files in ./course_files/
# 2. Ingest them:
python ingest_materials.py --dir ./course_files
```

### Add Piazza Q&A History

```bash
# Index all past questions with accepted answers:
python ingest_piazza.py
```

The bot will now reference these materials when generating answers.



## Core Files

| File | Purpose |
|------|---------|
| `bot.py` | Main polling loop and orchestration |
| `ai_answerer.py` | Claude API integration for answer generation |
| `piazza_client.py` | Piazza API wrapper and filtering logic |
| `db.py` | SQLite database for tracking answered questions |
| `config.py` | Application settings and constants |
| `ingest_materials.py` | CLI to add course files to knowledge base |
| `ingest_piazza.py` | CLI to add Piazza history to knowledge base |
| `rag/` | RAG (Retrieval-Augmented Generation) module for smart context |



## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software, provided you include the original license and copyright notice.

See the [LICENSE](LICENSE) file for full details.

## Disclaimer

**This tool is provided for educational use only and is accessed at your own risk. Outputs may contain inaccuracies and must be independently reviewed prior to posting. Written instructor authorization is required before deployment. Unauthorized use in violation of academic or platform policies is strictly prohibited.**
