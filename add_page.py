import os
import re
import sys
import logging
from pathlib import Path
import importlib.util
import subprocess
import click

# --- Constants ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
ROUTES_WEB_DIR = PROJECT_ROOT / "routes" / "web"
ROUTES_API_DIR = PROJECT_ROOT / "routes" / "api"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
ROUTER_PATH = PROJECT_ROOT / "routes" / "router.py"

# --- Logger ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("add_page")


# --- Utilities ---
def snake_to_pascal(name):
    return "".join(word.capitalize() for word in name.split("_"))


def pluralize(name):
    return name + "s" if not name.endswith("s") else name


def file_contains(path, pattern):
    if not path.exists():
        return False
    with open(path, "r") as f:
        return re.search(pattern, f.read()) is not None


def safe_write(path, content):
    if path.exists():
        click.echo(click.style(f"File already exists: {path}", fg="yellow"))
    else:
        with open(path, "w") as f:
            f.write(content)
        click.echo(click.style(f"Created {path}", fg="green"))


# --- CLI ---
@click.command()
@click.option("--name", required=True, help="Entity name in snake_case (e.g., contact)")
@click.option("--label", required=True, help="Human-readable label (e.g., Contact)")
@click.option("--fields", default="name", help="Comma-separated list of required fields (e.g., name,email)")
def main(name, label, fields):
    model_class = snake_to_pascal(name)
    table_name = pluralize(name)
    required_fields = [f.strip() for f in fields.split(",") if f.strip()]

    # 1. Create Model
    model_path = MODELS_DIR / f"{name}.py"
    if not model_path.exists():
        if click.confirm(f"Model not found. Create {model_path.name}?"):
            model_template = f"""from app.models.base import db, BaseModel

class {model_class}(db.Model, BaseModel):
    __tablename__ = '{table_name}'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<{model_class} {{self.name}}>
"""
            safe_write(model_path, model_template)

            init_path = MODELS_DIR / "__init__.py"
            with open(init_path, "a") as f:
                f.write(f"from .{name} import {model_class}\n")
            click.echo(click.style(f"Updated {init_path.name}", fg="blue"))

    # 2. Web Route
    web_route_path = ROUTES_WEB_DIR / f"{name}.py"
    if not web_route_path.exists():
        if click.confirm(f"Web route not found. Create {web_route_path.name}?"):
            web_template = f"""from app.models import {model_class}
from app.routes.web import {name}_bp
from app.routes.web.generic import GenericWebRoutes

{name}_routes = GenericWebRoutes(
    model={model_class},
    blueprint={name}_bp,
    index_template="{table_name}.html",
    required_fields={required_fields},
    unique_fields=[],
)
"""
            safe_write(web_route_path, web_template)

    # 3. API Route
    api_route_path = ROUTES_API_DIR / f"{name}.py"
    if not api_route_path.exists():
        if click.confirm(f"Add API route for {name}?"):
            api_template = f"""from app.models import {model_class}
from app.routes.api import api_{table_name}_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.crud_service import CRUDService

{table_name}_api_routes = GenericAPIRoutes(
    blueprint=api_{table_name}_bp,
    model={model_class},
    service=CRUDService({model_class}),
    api_prefix="/api/{table_name}",
    required_fields={required_fields},
    unique_fields=[],
)
"""
            safe_write(api_route_path, api_template)

    # 4. Template
    html_template_path = TEMPLATES_DIR / f"{table_name}.html"
    if not html_template_path.exists():
        if click.confirm(f"Add HTML template for {table_name}?"):
            html_template = f"""{{% extends 'pages/base/page.html' %}}

{{% block content %}}
  <h1>{label}</h1>
  {{% include 'pages/base/common/_table.html' %}}
{{% endblock %}}
"""
            safe_write(html_template_path, html_template)

    # 5. Table Config
    if click.confirm(f"Add a default TableConfig entry for '{table_name}'?"):
        click.echo(click.style("Attempting to set table config via Flask shell...", fg="yellow"))
        try:
            subprocess.run(
                [
                    "flask",
                    "shell",
                    "-c",
                    f"from app.models.table_config import TableConfig; TableConfig.set_config('{table_name}', {{'columns': []}})",
                ]
            )
        except Exception as e:
            click.echo(click.style(f"Failed to set TableConfig: {e}", fg="red"))

    # 6. Router Reminder
    if ROUTER_PATH.exists():
        if click.confirm("Do you want to be reminded to update router.py?"):
            click.echo(click.style(f"Don't forget to register {name} routes in {ROUTER_PATH.name}!", fg="magenta"))

    click.echo(click.style("✅ Done!", fg="green"))


if __name__ == "__main__":
    main()
