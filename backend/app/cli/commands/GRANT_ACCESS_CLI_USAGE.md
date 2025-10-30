# Grant Review Access CLI Commands

## Overview

These CLI commands allow you to manage user access to reviews in bulk, making it easy to grant or revoke access to all reviews from a specific company or all reviews in the system.

## Commands

### 1. Grant Company Access

Grant a user access to all reviews from a specific company.

```bash
python -m app.cli.main grant-company-access \
  --user-id <USER_ID> \
  --company-id <COMPANY_ID> \
  [--access-type <TYPE>] \
  [--is-owner]
```

**Options:**
- `--user-id` (required): User ID to grant access to
- `--company-id` (required): Company ID whose reviews to grant access to
- `--access-type` (optional): Type of access (default: "platform")
  - Common values: "platform", "shared", "uploaded"
- `--is-owner` (optional): Flag to mark user as owner of these reviews

**Example:**
```bash
# Grant user 1 access to all Spotify reviews
python -m app.cli.main grant-company-access --user-id 1 --company-id 1

# Grant user 2 access to all Netflix reviews as owner
python -m app.cli.main grant-company-access --user-id 2 --company-id 4 --is-owner

# Grant user 3 shared access to Slack reviews
python -m app.cli.main grant-company-access --user-id 3 --company-id 2 --access-type shared
```

### 2. Grant All Access

Grant a user access to ALL reviews in the entire system.

```bash
python -m app.cli.main grant-all-access \
  --user-id <USER_ID> \
  [--access-type <TYPE>] \
  [--is-owner]
```

**Options:**
- `--user-id` (required): User ID to grant access to
- `--access-type` (optional): Type of access (default: "platform")
- `--is-owner` (optional): Flag to mark user as owner of all reviews

**Example:**
```bash
# Grant user 1 access to all reviews in the system
python -m app.cli.main grant-all-access --user-id 1

# Grant admin user access to all reviews as owner
python -m app.cli.main grant-all-access --user-id 999 --is-owner --access-type admin
```

### 3. Revoke Company Access

Revoke a user's access to all reviews from a specific company.

```bash
python -m app.cli.main revoke-company-access \
  --user-id <USER_ID> \
  --company-id <COMPANY_ID>
```

**Options:**
- `--user-id` (required): User ID to revoke access from
- `--company-id` (required): Company ID whose reviews to revoke access to

**Example:**
```bash
# Revoke user 1's access to all Spotify reviews
python -m app.cli.main revoke-company-access --user-id 1 --company-id 1
```

## Common Workflows

### Setup: Give a new user access to platform reviews

```bash
# 1. Create the user
python -m app.cli.main create-user --email newuser@example.com

# 2. Get the user ID from the output (e.g., ID: 5)

# 3. Grant access to all platform reviews
python -m app.cli.main grant-all-access --user-id 5 --access-type platform
```

### Setup: Give a user access to specific company reviews

```bash
# Grant access to Spotify (company_id=1) and Netflix (company_id=4)
python -m app.cli.main grant-company-access --user-id 5 --company-id 1
python -m app.cli.main grant-company-access --user-id 5 --company-id 4
```

### Cleanup: Remove a user's access to a company

```bash
# Revoke access to Spotify reviews
python -m app.cli.main revoke-company-access --user-id 5 --company-id 1
```

## Output

Each command provides detailed output:

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

## Helper Commands

### List Users
```bash
python -m app.cli.main list-users
```

Shows all users with their IDs and emails.

### List Companies
```bash
python -m app.cli.main list-companies
```

Shows all companies with their IDs and review counts.

### List User Access
```bash
python -m app.cli.main list-user-access --user-id <USER_ID>
```

Shows detailed access report for a specific user:
- Total reviews accessible
- Breakdown by company
- Owned vs. shared reviews

### List All
```bash
python -m app.cli.main list-all
```

Shows both users and companies in one command.

## Finding IDs

### Get User ID
```bash
# List all users
python -m app.cli.main list-users

# Output example:
# ID:   1 | Email: john@example.com           | Username: john
# ID:   2 | Email: jane@example.com           | Username: jane
```

### Get Company ID
```bash
# List all companies
python -m app.cli.main list-companies

# Output example:
# ID:   1 | Name: Spotify              | Reviews:  150
# ID:   2 | Name: Slack                | Reviews:  120
# ID:   3 | Name: Notion               | Reviews:   80
# ID:   4 | Name: Netflix              | Reviews:  200
```

## Access Types

The `--access-type` parameter helps track how users got access:

- **platform**: Reviews available to all users (default for bulk grants)
- **uploaded**: User uploaded these reviews themselves
- **shared**: Reviews shared with the user by another user
- **admin**: Administrative access
- **custom**: Any custom type you define

## Notes

- The commands are idempotent - running them multiple times won't create duplicate access grants
- The output shows how many new grants were created vs. how many the user already had
- Use `--is-owner` flag when the user should be marked as the owner (e.g., they uploaded the reviews)
- All operations are logged for audit purposes

## Troubleshooting

### "User with ID X not found"
- Make sure the user exists: `python -m app.cli.main create-user --email user@example.com`

### "Company with ID X not found"
- Make sure companies are seeded: `python -m app.cli.main seed-companies`

### "No reviews found for company"
- Make sure reviews are ingested: `python -m app.cli.main ingest-mock`
