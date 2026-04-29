# Insighta CLI

Command-line interface for Insighta Labs+ platform.

## 🚀 Overview

The Insighta CLI provides a terminal-based interface to interact with the Insighta Labs+ backend API. It supports authentication, profile management, search, and data export.

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-org/insighta-cli.git
cd insighta-cli

# Install in editable mode
pip install -e .

# Or install globally
pip install .
```

## 🔐 Authentication

### Login

```bash
insighta login
```

This will:

1. Generate a PKCE code verifier and challenge
2. Open your browser to GitHub OAuth
3. Start a local callback server on port 8899
4. Capture the OAuth callback
5. Exchange the code for tokens
6. Store credentials in `~/.insighta/credentials.json`

### Logout

```bash
insighta logout
```

Revokes the refresh token server-side and clears local credentials.

### Who Am I?

```bash
insighta whoami
```

Displays the currently logged-in user's information.

## 📋 Profile Commands

### List Profiles

```bash
# Basic list
insighta profiles list

# With filters
insighta profiles list --gender male
insighta profiles list --country NG --age-group adult
insighta profiles list --min-age 25 --max-age 40

# With sorting
insighta profiles list --sort-by age --order desc

# With pagination
insighta profiles list --page 2 --limit 20
```

Options:

- `--gender`: Filter by gender (male/female)
- `--country`: Filter by country code (e.g., NG, US)
- `--age-group`: Filter by age group (child/teenager/adult/senior)
- `--min-age`: Minimum age
- `--max-age`: Maximum age
- `--sort-by`: Sort field (age, created_at, gender_probability, country_probability)
- `--order`: Sort order (asc/desc)
- `--page`: Page number
- `--limit`: Results per page (max 50)

### Get Profile

```bash
insighta profiles get <profile-id>
```

### Search Profiles

```bash
insighta profiles search "young males from nigeria"
insighta profiles search "females from US" --page 1 --limit 20
```

### Create Profile (Admin Only)

```bash
insighta profiles create --name "Harriet Tubman"
```

### Export Profiles

```bash
# Export all profiles as CSV
insighta profiles export --format csv

# Export with filters
insighta profiles export --format csv --gender male --country NG
insighta profiles export --format csv --min-age 25 --max-age 40
```

Exported files are saved to the current working directory.

## 🔧 Configuration

### Backend URL

By default, the CLI connects to `http://localhost:8000`. To use a different backend:

```bash
insighta login --backend https://your-api.example.com
```

Or set the environment variable:

```bash
export INSIGHTA_BACKEND_URL=https://your-api.example.com
```

### Credential Storage

Credentials are stored in `~/.insighta/credentials.json`:

```json
{
  "backend_url": "http://localhost:8000",
  "access_token": "...",
  "refresh_token": "...",
  "username": "your-username"
}
```

## 🔄 Token Handling

The CLI automatically handles token refresh:

- When an API request returns 401, the CLI automatically refreshes the token
- If refresh fails, you'll be prompted to log in again

## 🛠️ Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

## 📁 Project Structure

```
insighta-cli/
├── insighta/
│   ├── __init__.py
│   ├── api.py           # HTTP client with auto-refresh
│   ├── auth.py          # Login/logout/whoami commands
│   ├── cli.py           # Main CLI entry point
│   ├── credentials.py   # Credential storage
│   ├── output.py        # Rich console output
│   └── profiles.py      # Profile commands
├── pyproject.toml
└── README.md
```

## 📄 License

MIT License
