# CLI Grant Review Access - Summary

## What Was Created

I've created a complete CLI system for managing bulk user access to reviews. This allows you to easily grant or revoke access to reviews by company.

## Files Created

### 1. Main Command File
**`backend/app/cli/commands/grant_review_access.py`**
- `grant_company_reviews_access()` - Grant access to all reviews from a specific company
- `grant_all_reviews_access()` - Grant access to ALL reviews in the system
- `revoke_company_reviews_access()` - Revoke access to all reviews from a company

### 2. CLI Integration
**`backend/app/cli/main.py`** (updated)
Added three new CLI commands:
- `grant-company-access` - Grant company-specific access
- `grant-all-access` - Grant system-wide access
- `revoke-company-access` - Revoke company-specific access

### 3. Documentation
**`backend/app/cli/commands/GRANT_ACCESS_CLI_USAGE.md`**
- Complete usage guide
- Examples for all commands
- Common workflows
- Troubleshooting tips

### 4. Example Script
**`backend/app/cli/commands/grant_access_example.py`**
- Demonstrates the complete workflow
- Can be run directly for testing
- Shows integration patterns

## Usage Examples

### Grant access to all Spotify reviews
```bash
python -m app.cli.main grant-company-access --user-id 1 --company-id 1
```

### Grant access to all reviews in the system
```bash
python -m app.cli.main grant-all-access --user-id 1
```

### Grant access with ownership flag
```bash
python -m app.cli.main grant-company-access --user-id 1 --company-id 1 --is-owner
```

### Revoke access to company reviews
```bash
python -m app.cli.main revoke-company-access --user-id 1 --company-id 1
```

## Command Options

### grant-company-access
- `--user-id` (required): User ID to grant access to
- `--company-id` (required): Company ID whose reviews to grant access to
- `--access-type` (optional): Type of access (default: "platform")
- `--is-owner` (optional): Mark user as owner flag

### grant-all-access
- `--user-id` (required): User ID to grant access to
- `--access-type` (optional): Type of access (default: "platform")
- `--is-owner` (optional): Mark user as owner flag

### revoke-company-access
- `--user-id` (required): User ID to revoke access from
- `--company-id` (required): Company ID whose reviews to revoke

## Features

✅ **Bulk Operations**: Grant/revoke access to hundreds of reviews at once
✅ **Idempotent**: Safe to run multiple times - won't create duplicates
✅ **Detailed Logging**: Shows exactly what happened
✅ **Validation**: Checks that users and companies exist
✅ **Statistics**: Reports how many new grants vs. existing access
✅ **Flexible Access Types**: Track how users got access (platform, shared, uploaded, etc.)
✅ **Ownership Tracking**: Mark users as owners when appropriate

## Output Example

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

## Common Workflows

### Setup new user with platform access
```bash
# 1. Create user
python -m app.cli.main create-user --email newuser@example.com

# 2. Grant access to all reviews
python -m app.cli.main grant-all-access --user-id <USER_ID>
```

### Grant selective company access
```bash
# Give user access to Spotify and Netflix only
python -m app.cli.main grant-company-access --user-id 5 --company-id 1
python -m app.cli.main grant-company-access --user-id 5 --company-id 4
```

### Cleanup user access
```bash
# Remove access to specific company
python -m app.cli.main revoke-company-access --user-id 5 --company-id 1
```

## Integration with Existing System

This CLI integrates seamlessly with:
- ✅ `user_review_feedback` table (junction table)
- ✅ `UserReviewFeedbackRepository` (uses bulk_grant_access method)
- ✅ Existing user and company repositories
- ✅ Your logging standards
- ✅ Database session management

## Testing

Run the example script to test:
```bash
python backend/app/cli/commands/grant_access_example.py
```

Or use the CLI directly:
```bash
# Make sure you have data first
python -m app.cli.main seed-companies
python -m app.cli.main ingest-mock
python -m app.cli.main create-user --email test@example.com

# Then grant access
python -m app.cli.main grant-company-access --user-id 1 --company-id 1
```

## Next Steps

1. Run migrations to create the `user_review_feedback` table:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. Seed your database:
   ```bash
   python -m app.cli.main seed-companies
   python -m app.cli.main ingest-mock
   ```

3. Create a test user:
   ```bash
   python -m app.cli.main create-user --email test@example.com
   ```

4. Grant access:
   ```bash
   python -m app.cli.main grant-all-access --user-id 1
   ```

5. Verify in your application that the user can now access the reviews!

## Notes

- Commands are safe to run multiple times (idempotent)
- All operations are logged for audit purposes
- Access types help track provenance of access grants
- The `is_owner` flag distinguishes uploaded vs. shared reviews
- Bulk operations are optimized for performance
