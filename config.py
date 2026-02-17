# Piazza-Chimp Configuration
# Tuneable constants for bot behavior

POLL_INTERVAL_SEC = 60  # seconds between Piazza poll cycles
PIAZZA_CALL_SLEEP = 2   # seconds between individual Piazza API calls (rate limiting)

ANTHROPIC_MAX_TOKENS = 800
MODEL = "claude-haiku-4-5-20251001"

DB_PATH = "piazza_bot.db"

AI_DISCLAIMER = "\n\n---\n*AI-generated draft — please verify with course staff.*"
