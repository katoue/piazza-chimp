# CI/CD Pipeline

This project uses GitHub Actions for automated testing, linting, and security checks.

## Workflows

### 1. Tests (`test.yml`)

**Triggers:** On push and pull requests to `master` or `main`

**What it does:**
- Tests on Python 3.8, 3.9, 3.10, 3.11
- Checks code style with flake8
- Tests all module imports
- Validates embedder functionality (384 dimensions)
- Verifies configuration constants

**Status Badge:**
```markdown
![Tests](https://github.com/katoue/piazza-chimp/actions/workflows/test.yml/badge.svg)
```

### 2. Lint & Format Check (`lint.yml`)

**Triggers:** On push and pull requests

**What it does:**
- Checks code style with flake8
- Verifies formatting with black
- Checks import sorting with isort

**Status Badge:**
```markdown
![Lint](https://github.com/katoue/piazza-chimp/actions/workflows/lint.yml/badge.svg)
```

### 3. Security & Dependencies (`security.yml`)

**Triggers:** On push, pull requests, and daily schedule

**What it does:**
- Runs bandit for security vulnerabilities
- Checks dependencies with safety
- Scheduled daily scan for new vulnerabilities

**Status Badge:**
```markdown
![Security](https://github.com/katoue/piazza-chimp/actions/workflows/security.yml/badge.svg)
```

## Local Development

To run the same checks locally before pushing:

```bash
# Install dev dependencies
pip install flake8 black isort bandit safety pytest

# Run linting
flake8 .
black --check .
isort --check-only .

# Run security checks
bandit -r . -ll
safety check

# Test imports
python -c "import bot; import ai_answerer; import piazza_client"
```

## View Results

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select a workflow to see results
4. Red ❌ = Failed, Green ✅ = Passed

## Customization

Edit workflow files in `.github/workflows/` to:
- Add more Python versions to test
- Change linting rules
- Add deployment steps
- Modify schedules
