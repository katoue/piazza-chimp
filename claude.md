# Claude Instructions for piazza-chimp

## Project Overview
piazza-chimp is a bot implementation for interacting with Piazza. The project uses `.env` file for credentials management instead of a secrets.py file.

## Key Guidelines

### Code Style & Standards
- Keep changes minimal and focused on the requested task
- Avoid over-engineering solutions
- Prefer editing existing files to creating new ones
- Don't add unnecessary comments, docstrings, or type annotations unless modifying that code

### Credentials & Security
- Credentials are stored in `.env` file (not in version control)
- Never commit `.env` or credentials to git
- Use environment variables via `python-dotenv` for configuration

### Git Workflow
- Always confirm before pushing to remote
- Commit changes when explicitly requested by the user
- Use clear, concise commit messages
- Don't force push unless explicitly authorized

### Testing & Verification
- Test changes before considering them complete
- Ask before running destructive operations
- Investigate root causes rather than bypassing safety checks

### File Structure
- Primary client code: `piazza_client.py`
- Configuration: `.env` (gitignored)
- Documentation: `README.md`

## Important Reminders
- Always read existing code before proposing modifications
- Don't commit files without explicit user request
- Ask for confirmation on risky or irreversible actions
- Keep solutions simple and focused on the task at hand
