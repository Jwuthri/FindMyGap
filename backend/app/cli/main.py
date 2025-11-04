"""
Main CLI entry point using Click.
"""

import asyncio

import click

from app import get_logger

logger = get_logger(__name__)


@click.group()
def cli():
    """FindMyGap CLI - Database and data management tools."""
    pass


@cli.command()
def create_db():
    """Create the database if it doesn't exist."""
    from scripts.create_database import create_database
    success = create_database()
    if not success:
        click.echo("Failed to create database", err=True)
        exit(1)
    click.echo("✅ Database ready")


@cli.command()
def init_db():
    """Initialize database with tables and sample data."""
    from app.cli.commands.init_database import init_database
    asyncio.run(init_database())


@cli.command()
def ingest_mock():
    """Ingest mock review data."""
    from app.cli.commands.ingest_mock import ingest_mock_data
    ingest_mock_data()


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--user-id', default=1, help='User ID')
def ingest_file(file_path, user_id):
    """Ingest a data file (CSV, Excel, JSON, Parquet)."""
    from app.cli.commands.ingest_file import ingest_data_file
    asyncio.run(ingest_data_file(file_path, user_id))


@cli.command()
@click.option('--user-id', default=None, help='User ID to filter datasets')
def view_schemas(user_id):
    """View all available schemas."""
    from app.cli.commands.view_schemas import view_platform_metadata
    view_platform_metadata(user_id)


@cli.command()
def setup_platform():
    """Setup platform datasets with metadata."""
    from app.cli.commands.setup_platform import setup_platform_datasets
    asyncio.run(setup_platform_datasets())


@cli.command()
@click.option('--email', required=True, help='User email')
@click.option('--username', default=None, help='Username (defaults to email prefix)')
@click.option('--full-name', default=None, help='Full name')
def create_user(email, username, full_name):
    """Create a new user."""
    from app.cli.commands.create_user import create_user as create_user_cmd
    user = create_user_cmd(email, username, full_name)
    if user:
        click.echo(f"✅ Created user: {user.id} - {user.email}")
    else:
        click.echo("❌ Failed to create user", err=True)
        exit(1)


@cli.command()
@click.option('--name', required=True, help='Company name')
@click.option('--description', default=None, help='Company description')
@click.option('--industry', default=None, help='Industry')
@click.option('--website', default=None, help='Website URL')
def create_company(name, description, industry, website):
    """Create a new company."""
    from app.cli.commands.create_company import create_company as create_company_cmd
    company = create_company_cmd(name, description, industry, website)
    if company:
        click.echo(f"✅ Company: {company.id} - {company.name}")
    else:
        click.echo("❌ Failed to create company", err=True)
        exit(1)


@cli.command()
def seed_companies():
    """Seed default companies (Spotify, Slack, Notion, Netflix)."""
    from app.cli.commands.seed_companies import seed_companies as seed_cmd
    success = seed_cmd()
    if not success:
        click.echo("❌ Failed to seed companies", err=True)
        exit(1)


@cli.command()
@click.option('--user-id', required=True, type=int, help='User ID to grant access to')
@click.option('--company-name', required=True, help='Company name whose reviews to grant access to')
def grant_company_access(user_id, company_name):
    """Grant a user access to all reviews from a specific company (copies reviews)."""
    from app.cli.commands.grant_review_access import grant_company_reviews_access
    success = grant_company_reviews_access(user_id, company_name)
    if not success:
        click.echo("❌ Failed to grant access", err=True)
        exit(1)


@cli.command()
@click.option('--user-id', required=True, type=int, help='User ID to grant access to')
def grant_all_access(user_id):
    """Grant a user access to ALL reviews in the system (copies reviews)."""
    from app.cli.commands.grant_review_access import grant_all_reviews_access
    success = grant_all_reviews_access(user_id)
    if not success:
        click.echo("❌ Failed to grant access", err=True)
        exit(1)


@cli.command()
@click.option('--user-id', required=True, type=int, help='User ID to revoke access from')
@click.option('--company-name', required=True, help='Company name whose reviews to revoke access to')
def revoke_company_access(user_id, company_name):
    """Revoke a user's access to all reviews from a specific company (deletes review copies)."""
    from app.cli.commands.grant_review_access import revoke_company_reviews_access
    success = revoke_company_reviews_access(user_id, company_name)
    if not success:
        click.echo("❌ Failed to revoke access", err=True)
        exit(1)


@cli.command()
def list_users():
    """List all users with their IDs."""
    from app.cli.commands.list_entities import list_users as list_users_cmd
    list_users_cmd()


@cli.command()
def list_companies():
    """List all companies with their IDs and review counts."""
    from app.cli.commands.list_entities import list_companies as list_companies_cmd
    list_companies_cmd()


@cli.command()
@click.option('--user-id', required=True, type=int, help='User ID to check access for')
def list_user_access(user_id):
    """List all reviews a user has access to, grouped by company."""
    from app.cli.commands.list_entities import list_user_access as list_user_access_cmd
    list_user_access_cmd(user_id)


@cli.command()
def list_all():
    """List all users and companies."""
    from app.cli.commands.list_entities import list_all as list_all_cmd
    list_all_cmd()


@cli.command()
@click.option('--table', required=True, help='Table name to generate EDA for')
def generate_eda(table):
    """Generate EDA for a specific table using LLM."""
    from app.cli.commands.generate_eda import generate_eda_for_table
    asyncio.run(generate_eda_for_table(table))


@cli.command()
@click.option('--tables', multiple=True, help='Specific tables to refresh (optional)')
def refresh_eda(tables):
    """Refresh EDA for all tables or specific tables."""
    from app.cli.commands.generate_eda import refresh_all_eda
    table_list = list(tables) if tables else None
    asyncio.run(refresh_all_eda(table_list))


@cli.command()
@click.option('--table', required=True, help='Table name to view EDA for')
def view_eda(table):
    """View EDA for a table."""
    from app.cli.commands.generate_eda import view_eda as view_eda_cmd
    view_eda_cmd(table)


if __name__ == '__main__':
    cli()
