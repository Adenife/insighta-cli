"""
cli.py — Main entry point for the insighta CLI tool.
"""
import click

from .auth import login_cmd, logout_cmd, whoami_cmd
from .profiles import profiles_group


@click.group()
@click.version_option("1.0.0", prog_name="insighta")
def main():
    """
    \b
    Insighta Labs+ CLI
    ──────────────────
    Interact with the Insighta Labs+ backend.
    Authenticate, query profiles, and export data — all from your terminal.

    Run 'insighta login' to get started.
    """


main.add_command(login_cmd, name="login")
main.add_command(logout_cmd, name="logout")
main.add_command(whoami_cmd, name="whoami")
main.add_command(profiles_group, name="profiles")


if __name__ == "__main__":
    main()
