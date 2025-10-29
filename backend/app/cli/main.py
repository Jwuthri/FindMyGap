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
@click.option('--user-id', default='user_123', help='User ID')
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


if __name__ == '__main__':
    cli()
