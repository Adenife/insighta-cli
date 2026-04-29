"""
output.py — Rich-powered tables, spinners, and error formatting.
"""
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from contextlib import contextmanager

console = Console()


@contextmanager
def spinner(message: str):
    """Display a spinner while work is happening."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(message, total=None)
        yield


def print_success(message: str):
    rprint(f"[bold green]✓[/bold green] {message}")


def print_error(message: str):
    rprint(f"[bold red]✗[/bold red] {message}")


def print_info(message: str):
    rprint(f"[bold cyan]ℹ[/bold cyan] {message}")


def print_profiles_table(profiles: list[dict]):
    """Render a list of profile dicts as a rich table."""
    if not profiles:
        print_info("No profiles found.")
        return

    table = Table(
        title="Profiles",
        show_header=True,
        header_style="bold magenta",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Gender", style="green")
    table.add_column("Age", style="yellow", justify="right")
    table.add_column("Age Group", style="blue")
    table.add_column("Country", style="magenta")
    table.add_column("Gender Prob.", justify="right")
    table.add_column("ID", style="dim", no_wrap=True)

    for p in profiles:
        table.add_row(
            p.get("name", ""),
            p.get("gender", ""),
            str(p.get("age", "")),
            p.get("age_group", ""),
            f"{p.get('country_name') or p.get('country_id', '')} ({p.get('country_id', '')})",
            f"{float(p.get('gender_probability', 0)):.0%}",
            str(p.get("id", ""))[:8] + "...",
        )

    console.print(table)


def print_profile_detail(p: dict):
    """Render a single profile as a key/value table."""
    table = Table(show_header=False, border_style="dim", show_lines=True)
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="white")

    fields = [
        ("ID", str(p.get("id", ""))),
        ("Name", p.get("name", "")),
        ("Gender", p.get("gender", "")),
        ("Gender Probability", f"{float(p.get('gender_probability', 0)):.0%}"),
        ("Age", str(p.get("age", ""))),
        ("Age Group", p.get("age_group", "")),
        ("Country", f"{p.get('country_name') or ''} ({p.get('country_id', '')})"),
        ("Country Probability", f"{float(p.get('country_probability', 0)):.0%}"),
        ("Created At", str(p.get("created_at", ""))),
    ]
    for k, v in fields:
        table.add_row(k, v)

    console.print(table)


def print_pagination(page: int, limit: int, total: int, total_pages: int):
    console.print(
        f"\n[dim]Page {page}/{total_pages} · {total} total results · {limit}/page[/dim]"
    )
