"""
profiles.py — CLI profile sub-commands.
"""
import os
from datetime import datetime
from pathlib import Path

import click

from . import api
from .output import (
    console,
    print_info,
    print_pagination,
    print_profile_detail,
    print_profiles_table,
    spinner,
)


@click.group("profiles")
def profiles_group():
    """Manage and query profiles."""


@profiles_group.command("list")
@click.option("--gender", default=None, help="Filter by gender (male/female)")
@click.option("--country", default=None, help="Filter by country code (e.g. NG)")
@click.option("--age-group", default=None, help="Filter by age group (child/teenager/adult/senior)")
@click.option("--min-age", default=None, type=int, help="Minimum age")
@click.option("--max-age", default=None, type=int, help="Maximum age")
@click.option("--sort-by", default="created_at", help="Sort field (age, created_at, gender_probability, country_probability)")
@click.option("--order", default="desc", type=click.Choice(["asc", "desc"]), help="Sort order")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--limit", default=10, type=int, help="Results per page (max 50)")
def list_profiles(gender, country, age_group, min_age, max_age, sort_by, order, page, limit):
    """List profiles with optional filters and sorting."""
    params = {
        k: v for k, v in {
            "gender": gender,
            "country_id": country,
            "age_group": age_group,
            "min_age": min_age,
            "max_age": max_age,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit,
        }.items() if v is not None
    }

    with spinner("Fetching profiles…"):
        data = api.request("GET", "/api/profiles", params=params)

    print_profiles_table(data.get("data", []))
    print_pagination(
        data.get("page", page),
        data.get("limit", limit),
        data.get("total", 0),
        data.get("total_pages", 1),
    )


@profiles_group.command("get")
@click.argument("id")
def get_profile(id):
    """Get a single profile by UUID."""
    with spinner(f"Fetching profile {id}…"):
        data = api.request("GET", f"/api/profiles/{id}")

    print_profile_detail(data.get("data", {}))


@profiles_group.command("search")
@click.argument("query")
@click.option("--page", default=1, type=int)
@click.option("--limit", default=10, type=int)
def search_profiles(query, page, limit):
    """Search profiles using natural language (e.g. 'young males from nigeria')."""
    with spinner(f"Searching: '{query}'…"):
        data = api.request("GET", "/api/profiles/search", params={"q": query, "page": page, "limit": limit})

    print_profiles_table(data.get("data", []))
    print_pagination(
        data.get("page", page),
        data.get("limit", limit),
        data.get("total", 0),
        data.get("total_pages", 1),
    )


@profiles_group.command("create")
@click.option("--name", required=True, help="Name for the profile")
def create_profile(name):
    """Create a new profile (admin only). Fetches gender, age, and nationality data."""
    with spinner(f"Creating profile for '{name}'…"):
        data = api.request("POST", "/api/profiles", json={"name": name})

    profile = data.get("data", {})
    print_profile_detail(profile)
    if data.get("message"):
        print_info(data["message"])


@profiles_group.command("export")
@click.option("--format", "fmt", default="csv", type=click.Choice(["csv"]), help="Export format")
@click.option("--gender", default=None)
@click.option("--country", default=None)
@click.option("--age-group", default=None)
@click.option("--min-age", default=None, type=int)
@click.option("--max-age", default=None, type=int)
@click.option("--sort-by", default="created_at")
@click.option("--order", default="desc", type=click.Choice(["asc", "desc"]))
def export_profiles(fmt, gender, country, age_group, min_age, max_age, sort_by, order):
    """Export profiles as CSV, saved to the current directory."""
    params = {
        k: v for k, v in {
            "format": fmt,
            "gender": gender,
            "country_id": country,
            "age_group": age_group,
            "min_age": min_age,
            "max_age": max_age,
            "sort_by": sort_by,
            "order": order,
        }.items() if v is not None
    }

    with spinner("Exporting profiles…"):
        resp = api.request("GET", "/api/profiles/export", params=params, stream=True)

    # Extract filename from Content-Disposition header or generate one
    disposition = resp.headers.get("content-disposition", "")
    filename = None
    if 'filename="' in disposition:
        filename = disposition.split('filename="')[1].rstrip('"')
    if not filename:
        filename = f"profiles_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    save_path = Path(os.getcwd()) / filename
    save_path.write_bytes(resp.content)

    console.print(f"[bold green]✓[/bold green] Exported to [cyan]{save_path}[/cyan]")
