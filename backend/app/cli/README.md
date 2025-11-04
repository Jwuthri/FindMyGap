# FindMyGap CLI Reference

Complete guide for database and data management CLI commands.

## Installation

```bash
cd backend
pip install click
```

## Quick Start

```bash
# Initialize database with sample data
python -m app.cli.main init-db

# Seed default companies
python -m app.cli.main seed-companies

# Create a user
python -m app.cli.main create-user --email user@example.com

# View all available commands
python -m app.cli.main --help
```

## Database Commands

### Initialize Database

Creates tables and loads sample data (default user, mock reviews, sample conversations).

```bash
python -m app.cli.main init-db
```

### Create Database

Creates the database if it doesn't exist.

```bash
python -m app.cli.main create-db
```

## Data Ingestion Commands

### Ingest Mock Data

Ingests mock review data for testing.

```bash
python -m app.cli.main ingest-mock
```

### Ingest File

Ingests a data file (CSV, Excel, JSON, Parquet).

```bash
python -m app.cli.main ingest-file path/to/file.csv --user-id user_123
```

Options:

- `--user-id`: User ID to associate with the data (default: 1)

### Setup Platform Datasets

Sets up platform datasets with metadata.

```bash
python -m app.cli.main setup-platform
```

## User Management Commands

### Create User

Creates a new user.

```bash
python -m app.cli.main create-user --email john@example.com --username john --full-name "John Doe"
```


## Eda table

### Refresh All Tables

```bash
# Refresh EDA for all tables
python -m app.cli refresh-eda

# Refresh specific tables
python -m app.cli refresh-eda --tables user_review_feedback --tables reviews_feedback
```

### View EDA

### Refresh All Tables

```bash
# Refresh EDA for all tables
python -m app.cli refresh-eda

# Refresh specific tables
python -m app.cli refresh-eda --tables user_review_feedback --tables reviews_feedback
```

### View EDA

```bash
# View EDA for a table
python -m app.cli view-eda --table user_review_feedback
```

### Generate EDA for a Table
```bash
python -m app.cli.main generate-eda --table user_review_feedback
```

Options:

- `--email` (required): User email
- `--username` (optional): Username (defaults to email prefix)
- `--full-name` (optional): Full name

Examples:

```bash
# Minimal
python -m app.cli.main create-user --email jane@example.com

# Full details
python -m app.cli.main create-user --email john@example.com --username john --full-name "John Doe"
```

### List Users

Lists all users with their IDs and emails.

```bash
python -m app.cli.main list-users
```

## Company Management Commands

### Create Company

Creates a new company.

```bash
python -m app.cli.main create-company --name "Spotify" --description "Music streaming" --industry "Technology" --website "https://spotify.com"
```

Options:

- `--name` (required): Company name
- `--description` (optional): Company description
- `--industry` (optional): Industry
- `--website` (optional): Website URL

Examples:

```bash
# Minimal
python -m app.cli.main create-company --name "Netflix"

# Full details
python -m app.cli.main create-company --name "Spotify" --description "Music streaming" --industry "Technology" --website "https://spotify.com"
```

### Seed Companies

Seeds default companies (Spotify, Slack, Notion, Netflix).

```bash
python -m app.cli.main seed-companies
```

### List Companies

Lists all companies with their IDs and review counts.

```bash
python -m app.cli.main list-companies
```

## Access Management Commands

### Grant Company Access

Grants a user access to all reviews from a specific company.

```bash
python -m app.cli.main grant-company-access --user-id 1 --company-id 1
```

Options:

- `--user-id` (required): User ID to grant access to
- `--company-id` (required): Company ID whose reviews to grant access to
- `--access-type` (optional): Type of access (default: "platform")
- `--is-owner` (optional): Flag to mark user as owner

Examples:

```bash
# Basic access
python -m app.cli.main grant-company-access --user-id 1 --company-id 1

# As owner
python -m app.cli.main grant-company-access --user-id 2 --company-id 4 --is-owner

# Shared access
python -m app.cli.main grant-company-access --user-id 3 --company-id 2 --access-type shared
```

### Grant All Access

Grants a user access to ALL reviews in the system.

```bash
python -m app.cli.main grant-all-access --user-id 1
```

Options:

- `--user-id` (required): User ID to grant access to
- `--access-type` (optional): Type of access (default: "platform")
- `--is-owner` (optional): Flag to mark user as owner

Examples:

```bash
# Platform access
python -m app.cli.main grant-all-access --user-id 1

# Admin access
python -m app.cli.main grant-all-access --user-id 999 --is-owner --access-type admin
```

### Revoke Company Access

Revokes a user's access to all reviews from a specific company.

```bash
python -m app.cli.main revoke-company-access --user-id 1 --company-id 1
```

Options:

- `--user-id` (required): User ID to revoke access from
- `--company-id` (required): Company ID whose reviews to revoke

### List User Access

Shows detailed access report for a specific user.

```bash
python -m app.cli.main list-user-access --user-id 1
```

### List All

Lists both users and companies in one command.

```bash
python -m app.cli.main list-all
```

## Schema Commands

### View Schemas

Views all available schemas.

```bash
python -m app.cli.main view-schemas
python -m app.cli.main view-schemas --user-id user_123
```

Options:

- `--user-id` (optional): User ID to filter datasets

## Common Workflows

### Initial Setup

```bash
# 1. Create database
python -m app.cli.main create-db

# 2. Initialize with sample data
python -m app.cli.main init-db

# 3. Seed companies
python -m app.cli.main seed-companies
```

### Create User with Access

```bash
# 1. Create user
python -m app.cli.main create-user --email newuser@example.com

# 2. Note the user ID from output (e.g., ID: 5)

# 3. Grant access to all platform reviews
python -m app.cli.main grant-all-access --user-id 5 --access-type platform
```

### Grant Selective Access

```bash
# Grant access to specific companies
python -m app.cli.main grant-company-access --user-id 5 --company-id 1
python -m app.cli.main grant-company-access --user-id 5 --company-id 4
```

### Ingest Custom Data

```bash
# 1. Ingest file
python -m app.cli.main ingest-file data/reviews.csv --user-id user_123

# 2. View schemas to confirm
python -m app.cli.main view-schemas --user-id user_123
```

## Access Types

The `--access-type` parameter tracks how users got access:

- **platform**: Reviews available to all users (default)
- **uploaded**: User uploaded these reviews themselves
- **shared**: Reviews shared with the user by another user
- **admin**: Administrative access
- **custom**: Any custom type you define

## Finding IDs

### Get User ID

```bash
python -m app.cli.main list-users
```

Output example:

```
ID:   1 | Email: john@example.com           | Username: john
ID:   2 | Email: jane@example.com           | Username: jane
```

### Get Company ID

```bash
python -m app.cli.main list-companies
```

Output example:

```
ID:   1 | Name: Spotify              | Reviews:  150
ID:   2 | Name: Slack                | Reviews:  120
ID:   3 | Name: Notion               | Reviews:   80
ID:   4 | Name: Netflix              | Reviews:  200
```

## Help

Get help for any command:

```bash
# General help
python -m app.cli.main --help

# Command-specific help
python -m app.cli.main create-user --help
python -m app.cli.main grant-company-access --help
```

## Notes

- Commands are idempotent - running them multiple times won't create duplicates
- All operations are logged for audit purposes
- Use `--is-owner` flag when the user should be marked as the owner
- Access grants show how many new grants were created vs. already existing

## Troubleshooting

**"User with ID X not found"**

```bash
python -m app.cli.main create-user --email user@example.com
```

**"Company with ID X not found"**

```bash
python -m app.cli.main seed-companies
```

**"No reviews found for company"**

```bash
python -m app.cli.main ingest-mock
```
