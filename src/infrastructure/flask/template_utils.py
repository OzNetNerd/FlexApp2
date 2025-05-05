# src/infrastructure/flask/template_utils.py

"""
Flask template utilities.

This module configures template globals, filters, and context processors.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def register_template_utils(app, navbar_entries):
    """
    Register template utilities including globals, filters, and context processors.

    Args:
        app: Flask application instance.
        navbar_entries: Dictionary of navigation bar entries.
    """

    @app.template_global()
    def now():
        """Get current UTC time.

        Returns:
            datetime: The current time in UTC timezone.
        """
        return datetime.now(ZoneInfo("UTC"))

    @app.context_processor
    def inject_navbar_entries():
        """Inject navigation bar entries into all templates.

        Returns:
            dict: Dictionary containing navbar entries.
        """
        return navbar_entries

    @app.template_filter("currencyfmt")
    def currencyfmt_filter(value):
        """Format the value as currency.

        Args:
            value: Numeric value to format as currency.

        Returns:
            str: Formatted currency string with symbol and thousand separators.
        """
        if value is None:
            return "N/A"

        # Get currency symbol from app config or use default
        currency_symbol = app.config.get("CURRENCY_SYMBOL", "$")

        # Format with thousand separators and 2 decimal places
        return f"{currency_symbol}{value:,.2f}"

    @app.context_processor
    def inject_globals():
        """Inject common variables into every template context.

        Returns:
            dict: Dictionary of common variables for templates.
        """
        return {
            "now": datetime.now(ZoneInfo("UTC")),
            "is_debug_mode": app.debug,
        }