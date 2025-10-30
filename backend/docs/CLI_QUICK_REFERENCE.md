# CLI Quick Reference - Review Access Management

## 🚀 Quick Start

```bash
# 1. Setup database
python -m app.cli.main create-db
python -m app.cli.main init-db
python -m app.cli.main seed-companies
python -m app.cli.main ingest-mock

# 2. Create a user
python -m app.cli.main create-user --email user@example.com

# 3. Grant access to all reviews
python -m app.cli.main grant-all-access --user-id 1

# 4. Verify access
python -m app.cli.main list-user-access --user-id 1
```

## 📋 List Commands

| Command | Description |
|---------|-------------|
| `list-users` | Show all users with IDs |
| `list-companies` | Show all companies with review counts |
| `list-user-access --user-id <ID>` | Show user's review access |
| `list-all` | Show both users and companies |

**Examples:**
```bash
python -m app.cli.main list-users
python -m app.cli.main list-companies
python -m app.cli.main list-user-access --user-id 1
```

## 🔑 Access Management Commands

### Grant Company Access
```bash
python -m app.cli.main grant-company-access \
  --user-id <USER_ID> \
  --company-id <COMPANY_ID> \
  [--access-type platform] \
  [--is-owner]
```

### Grant All Access
```bash
python -m app.cli.main grant-all-access \
  --user-id <USER_ID> \
  [--access-type platform] \
  [--is-owner]
```

### Revoke Company Access
```bash
python -m app.cli.main revoke-company-access \
  --user-id <USER_ID> \
  --company-id <COMPANY_ID>
```

## 💡 Common Use Cases

### New User Setup
```bash
# Create user
python -m app.cli.main create-user --email newuser@example.com

# Get user ID from output, then grant access
python -m app.cli.main grant-all-access --user-id <ID>
```

### Grant Selective Access
```bash
# Give access to Spotify and Netflix only
python -m app.cli.main grant-company-access --user-id 5 --company-id 1
python -m app.cli.main grant-company-access --user-id 5 --company-id 4
```

### Check User Access
```bash
# See what a user can access
python -m app.cli.main list-user-access --user-id 5
```

### Remove Access
```bash
# Revoke access to specific company
python -m app.cli.main revoke-company-access --user-id 5 --company-id 1
```

## 🏢 Company IDs (After Seeding)

| ID | Company |
|----|---------|
| 1  | Spotify |
| 2  | Slack   |
| 3  | Notion  |
| 4  | Netflix |

## 🎯 Access Types

| Type | Use Case |
|------|----------|
| `platform` | Reviews available to all users (default) |
| `uploaded` | User uploaded these reviews |
| `shared` | Reviews shared with user |
| `admin` | Administrative access |

## 📊 Example Output

### list-companies
```
============================================================
COMPANIES
============================================================

Found 4 companies:

  ID:   1 | Name: Spotify              | Reviews:  150
  ID:   2 | Name: Slack                | Reviews:  120
  ID:   3 | Name: Notion               | Reviews:   80
  ID:   4 | Name: Netflix              | Reviews:  200
```

### list-user-access
```
============================================================
USER ACCESS REPORT - User ID: 1
============================================================

User: john@example.com (ID: 1)

Total Reviews: 550
Companies: 4

  Spotify              -  150 reviews
  Slack                -  120 reviews
  Notion               -   80 reviews
  Netflix              -  200 reviews

Ownership:
  Owned:     0 reviews
  Shared:  550 reviews
```

### grant-company-access
```
============================================================
GRANTING BULK REVIEW ACCESS
============================================================
User: john@example.com (ID: 1)
Company: Spotify (ID: 1)
Found 150 reviews for Spotify
Granting access with type='platform', is_owner=False...

✅ Successfully granted access to 150 reviews
   User: john@example.com
   Company: Spotify
   Total Reviews: 150
   New Access Grants: 150
   Already Had Access: 0
```

## 🔧 All Available Commands

```bash
# Database
python -m app.cli.main create-db
python -m app.cli.main init-db

# Data Ingestion
python -m app.cli.main ingest-mock
python -m app.cli.main ingest-file <FILE_PATH> --user-id <ID>

# Setup
python -m app.cli.main seed-companies
python -m app.cli.main setup-platform

# User Management
python -m app.cli.main create-user --email <EMAIL>
python -m app.cli.main list-users

# Company Management
python -m app.cli.main create-company --name <NAME>
python -m app.cli.main list-companies

# Access Management
python -m app.cli.main grant-company-access --user-id <ID> --company-id <ID>
python -m app.cli.main grant-all-access --user-id <ID>
python -m app.cli.main revoke-company-access --user-id <ID> --company-id <ID>
python -m app.cli.main list-user-access --user-id <ID>

# Utilities
python -m app.cli.main view-schemas
python -m app.cli.main list-all
```

## 📝 Notes

- All commands are idempotent (safe to run multiple times)
- Use `--help` on any command for more details
- Check logs for detailed operation information
- IDs are auto-incremented integers st