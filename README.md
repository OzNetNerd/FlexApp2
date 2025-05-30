CRISP PROJECTION - OUR PLAN TO GET TO STRONGER CRISP
SALES TRAINING
LMS/Training system?


----

Create specialized service modules for common operations (data fetching, UI updates)
**Use event-based communication instead of direct DOM manipulation**
Consider using data attributes to decouple the JS from specific element IDs

Event systems:
Data fetching doesn't need to know about DOM structure
Multiple UI components can react to the same data update
Components can be added/removed without changing data code
Easier to test both layers independently

----
```
I have a Flask app. I want my 'web' code to pull data from the 'api' endpoints instead of the 'services' directly.

This is my tree:

```
app
├── __init__.py
├── app.py
├── graphql
│   ├── __init__.py
│   ├── dataloaders
│   │   ├── __init__.py
│   │   └── loaders.py
│   ├── resolvers
│   │   ├── __init__.py
│   │   ├── capability.py
│   │   ├── capability_category.py
│   │   ├── company.py
│   │   ├── company_capability.py
│   │   ├── contact.py
│   │   ├── crisp.py
│   │   ├── note.py
│   │   ├── opportunity.py
│   │   ├── setting.py
│   │   ├── srs.py
│   │   ├── task.py
│   │   └── user.py
│   ├── schema.py
│   └── types
│       ├── __init__.py
│       ├── capability.py
│       ├── capability_category.py
│       ├── company.py
│       ├── company_capability.py
│       ├── contact.py
│       ├── crisp.py
│       ├── note.py
│       ├── opportunity.py
│       ├── setting.py
│       ├── srs.py
│       ├── task.py
│       └── user.py
├── models
│   ├── __init__.py
│   ├── base.py
│   ├── capability.py
│   ├── capability_category.py
│   ├── company_capability.py
│   ├── mixins.py
│   ├── pages
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── contact.py
│   │   ├── crisp.py
│   │   ├── note.py
│   │   ├── opportunity.py
│   │   ├── setting.py
│   │   ├── srs.py
│   │   ├── task.py
│   │   └── user.py
│   ├── relationship.py
│   └── table_config.py
├── routes
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── companies.py
│   │   ├── contacts.py
│   │   ├── context.py
│   │   ├── json_utils.py
│   │   ├── notes.py
│   │   ├── opportunities.py
│   │   ├── relationships.py
│   │   ├── route_registration.py
│   │   ├── search.py
│   │   ├── srs.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── api_router.py
│   ├── base_context.py
│   ├── web
│   │   ├── __init__.py
│   │   ├── pages
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── companies
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── statistics.py
│   │   │   │   └── views.py
│   │   │   ├── contacts
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── statistics.py
│   │   │   │   └── views.py
│   │   │   ├── crisp.py
│   │   │   ├── home
│   │   │   │   ├── __init__.py
│   │   │   │   └── home.py
│   │   │   ├── opportunities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── statistics.py
│   │   │   │   └── views.py
│   │   │   ├── settings.py
│   │   │   ├── srs
│   │   │   │   ├── __init__.py
│   │   │   │   ├── batch.py
│   │   │   │   ├── blueprint.py
│   │   │   │   ├── cards.py
│   │   │   │   ├── contexts.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── review.py
│   │   │   │   └── views.py
│   │   │   ├── tasks
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── statistics.py
│   │   │   │   └── views.py
│   │   │   ├── users
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── statistics.py
│   │   │   │   └── views.py
│   │   │   └── users.py
│   │   └── utils
│   │       ├── __init__.py
│   │       ├── autocomplete.py
│   │       ├── blueprint_factory.py
│   │       ├── context.py
│   │       ├── json_validator.py
│   │       ├── relationships.py
│   │       ├── route_registration.py
│   │       ├── template_config.py
│   │       └── template_renderer.py
│   └── web_router.py
├── services
│   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── password.py
│   │   ├── session.py
│   │   └── view.py
│   ├── company
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── core.py
│   ├── contact
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── core.py
│   ├── crud_service.py
│   ├── note
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── search.py
│   ├── opportunity
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   ├── core.py
│   │   └── forecast.py
│   ├── relationship
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── query.py
│   │   └── types.py
│   ├── search
│   │   └── __init__.py
│   ├── service_base.py
│   ├── srs
│   │   ├── __init__.py
│   │   ├── algorithm.py
│   │   ├── analytics.py
│   │   ├── categories.py
│   │   ├── constants.py
│   │   ├── core.py
│   │   ├── filters.py
│   │   └── navigation.py
│   ├── task
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── core.py
│   ├── user
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── core.py
│   └── validator_mixin.py
└── utils
    ├── app_logging.py
    ├── model_registry.py
    └── router_utils.py

31 directories, 162 files
```

```



```
Route Audit Plan
Step 1: Examine API Routes First
Check these files to understand available API endpoints:

/app/routes/api/companies.py
/app/routes/api/contacts.py
/app/routes/api/opportunities.py
/app/routes/api/tasks.py
/app/routes/api/notes.py
/app/routes/api/users.py
/app/routes/api/srs.py

For each file, note:

Available endpoints
Parameters they accept
Return formats

Step 2: Check Web Route Implementations
Examine corresponding web route files:

/app/routes/web/pages/companies/views.py
/app/routes/web/pages/contacts/views.py
/app/routes/web/pages/opportunities/views.py
/app/routes/web/pages/tasks/views.py
/app/routes/web/pages/srs/views.py
/app/routes/web/pages/users.py

Look for:

Direct imports from /app/services/ (indicates potential issue)
API calls using patterns like requests, fetch, or internal HTTP clients
Proper error handling for API responses

Step 3: Fix Problematic Routes
For each route using services directly:

Find the matching API endpoint or create one
Replace direct service calls with API calls
Update error handling
Test thoroughly

Step 4: Create Helper Methods
Add utility methods in /app/routes/web/utils/ to standardize API calls.
Step 5: Verify Dashboard/Statistics Routes
Check special cases:

/app/routes/web/pages/*/dashboard.py
/app/routes/web/pages/*/statistics.py

These often need aggregated data and may need special handling.
```



# Harness

```
 git push https://username:$HARNESS_GIT_TOKEN@git.harness.io/oNOg8zc5RHyb-7VNI5dloQ/default/FlexApp2/FlexApp2.git main
```

# Repomix

```
docker run -v "$(pwd)":/app -it --rm ghcr.io/yamadashy/repomix --style markdown
```

```
clear && flask --app app.app run
```

# Tree

```
 clear &&  tree -P '*.py' -P '*.html' -P '*.js' -P *.css -I 'venv' --prune
```


Commands

```
# 1. Black (formatting)
pre-commit run black --all-files

# 2. isort (import sorting)
pre-commit run isort --all-files

# 3. Flake8 (+ bugbear, annotations, docstrings)
pre-commit run flake8 --all-files

# 4. mypy (static type checking)
pre-commit run mypy --all-files

# 5. pydocstyle (docstring conventions)
pre-commit run pydocstyle --all-files

# 6. bandit (security lint)
pre-commit run bandit --all-files

# 7. safety (dependency CVE scan)
pre-commit run python-safety-dependencies-check --all-files

# 8. detect-secrets (secret-scanning)
pre-commit run detect-secrets --all-files

# 9. pre-commit-hooks (whitespace, merge conflicts, large files, YAML)
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files
pre-commit run check-merge-conflict --all-files
pre-commit run check-added-large-files --all-files
pre-commit run check-yaml --all-files
```

# Change

```
This is my flask app. I want to focus on being DRY and consistent. Review the code and give me succinct info on what I need to do to achieve this.

This was some of your suggestions previously. We've implemented some. Check the code and pick up where we left off.

Take it one step at a time. do not overload me with steps/info. If changes are small, give me a fully updated func so I can paste over existing code. I fhtere's numerous changes in one file, givem e the entire file updated.

Give me a summary of the changes we're going to do with a succinct explanation of each. Then, with each change, tell me what file(s) we'll need, what the change(s) are, and why they're being done

```

# Change Recommendations

```
Here are the key areas to tighten up for DRYness and consistency across your Flask CRM:

Unify CRUD registration
– Replace all per-module ApiCrudRouteConfig/register_api_crud_routes calls with a loop in app/routes/api_router.py that auto-discovers (ENTITY_NAME, blueprint, service) tuples.
– Do the same in app/routes/web_router.py for your web-side blueprints and CrudRouteConfig.

Centralize template paths
– Define a naming convention (e.g. pages/<entity_plural>/<action>.html) and supply only entity names to CrudTemplates; let a factory build full paths.
– This removes repeated literals like "pages/crud/create_view_edit_srs_item.html" in each module.

Consolidate service logic
– Keep per-model validation in your ValidatorMixin, but collapse all simple NoteService, TaskService, etc. into one CRUDService subclass with an overridable required_fields list.
– Move any custom query methods (get_due_items, date filters, etc.) into dedicated service mixins rather than littering controllers.

Abstract search and filtering
– Create a generic SearchService that accepts model classes and search-fields arrays, replacing the hand-coded routes in app/routes/api/search.py.
– Or parameterize a single /api/search/<entity> endpoint.

DRY up context builders
– Rather than manually instantiating TableWebContext, ListApiContext, etc., in each handler, write a decorator (e.g. @use_context(TableWebContext, "Company")) that wraps your view.

Eliminate duplicate imports/loggers
– Configure a module-level logger factory (e.g. in app_logging.py) so you can drop logger = logging.getLogger(__name__) from every file.

Standardize error and JSON responses
– Consolidate json_response and error handlers into a single extension (blueprint or flask extension), so individual routes never call json_response directly.

Leverage introspection/factories
– For all your simple models (Company, Contact, etc.), generate API and web routes via a factory function that takes just the model class and optional overrides, removing boilerplate in each *.py.

Enforce code style and linting
– Adopt Black/flake8 with consistent import ordering and line-length limits so every file looks uniform.

Extract constants
– Move repeated magic strings ("Company", "Contacts", URL prefixes) into a single constants.py or into model metadata.
```

# Research
Defensive programming?

# todo

replace `render_template` with `render_safely`

# SImplified code - register_page_route

```
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from flask import Blueprint

@dataclass
class RouteConfig:
    url: str
    template_path: str
    title: str
    endpoint: Optional[str] = None
    methods: List[str] = field(default_factory=lambda: ["GET"])
    context_provider: Optional[Callable] = None
    error_message: str = "Failed to load the page"

    def __post_init__(self):
        """Derive endpoint name from template path if not provided"""
        if not self.endpoint:
            parts = self.template_path.split('/')
            if len(parts) > 1:
                # For nested templates (e.g., "users/profile.html")
                self.endpoint = f"{parts[-2]}_{parts[-1].split('.')[0]}"
            else:
                # For top-level templates (e.g., "home.html")
                self.endpoint = self.template_path.split('.')[0]

            logger.info(f"No endpoint provided. Using derived endpoint: '{self.endpoint}'")
        else:
            logger.info(f"Using provided endpoint: '{self.endpoint}'")

        logger.info(f"Route configuration prepared: URL='{self.url}', endpoint='{self.endpoint}', methods={self.methods}")
```

register_page_route

```
def register_page_route(blueprint: Blueprint, config: RouteConfig):
    """Register a route that renders a specific template with optional context."""
    def route_handler(*args, **kwargs):
        """Handle requests to this route by rendering the template with context."""
        logger.info(f"Handling request for endpoint '{config.endpoint}' with args={args}, kwargs={kwargs}")

        # If a context provider was specified, call it to get template data
        if config.context_provider:
            logger.info(f"Calling context provider for endpoint '{config.endpoint}'")
            context = config.context_provider(title=config.title, *args, **kwargs)
            if not context:
                logger.warning(f"Context provider returned None for endpoint '{config.endpoint}'")
                context = WebContext(title=config.endpoint)
        else:
            logger.info(f"No context provider for endpoint '{config.endpoint}', using default WebContext")
            context = WebContext(title=config.title)  # Using title instead of endpoint name

        # Render the template safely, handling exceptions
        return render_safely(
            config.template_path,
            context,
            config.error_message,
            endpoint_name=config.endpoint
        )

    # Set the function name for Flask (needed for proper endpoint registration)
    route_handler.__name__ = config.endpoint

    # Register the route with Flask
    blueprint.add_url_rule(
        config.url,
        endpoint=config.endpoint,
        view_func=route_handler,
        methods=config.methods
    )

    logger.info(f"Registered route '{config.endpoint}' at '{config.url}' for template '{config.template_path}' with methods {config.methods}")

    return route_handler
```

```
config = RouteConfig(
    url='/users',
    template_path='users/index.html',
    title='User List'
)
register_page_route(my_blueprint, config)
```

# Request Flow

```
+---------------------------------------------------------------+
|                          User Browses                        |
|            (Visits URL e.g., '/opportunities/1')              |
+---------------------------------------------------------------+
                          |
                          v
          +----------------------------------------------------+
          |       Flask Web Route Handler (e.g., /view/<id>)  |
          |   (Triggered by user browsing to the route)       |
          +----------------------------------------------------+
                          |
                          v
          +----------------------------------------------------+
          |       register_crud_routes (CRUD routes reg.)     |
          |   (Called with opportunities_bp, "Opportunity",   |
          |        and opportunity_service as params)          |
          +----------------------------------------------------+
                          |
                          v
          +---------------------------------------------+
          |        context_providers (Dictionary)       |
          |  (Defines lambdas for each CRUD action)    |
          +---------------------------------------------+
                          |
    +---------------------+---------------------+
    |                                           |
    v                                           v
+-------------------+                       +-------------------+
| 'view' Lambda     |                       | 'edit' Lambda     |
| (calls _get_entity_context)                | (calls _get_entity_context)   |
+-------------------+                       +-------------------+
         |                                            |
         v                                            v
+---------------------------------------------------------------+
|                _get_entity_context (retrieves entity data)     |
|  (Uses opportunity_service.get_by_id(entity_id))               |
|         (Service layer to fetch data from the database)         |
+---------------------------------------------------------------+
         |                                            |
         v                                            v
+---------------------------------------------------------------+
|  Returns context object (TableWebContext or TableWebContext)        |
|       Passes data to Jinja template for rendering               |
+---------------------------------------------------------------+
         |
         v
   Template Rendering
         |
         v
+---------------------------------------------------------------+
|               Flask Web Route - e.g., /opportunities/1        |
|   (User browses to '/opportunities/<entity_id>' URL)           |
|   - URL triggers the route and processes via the lambda       |
|   - Returns the context to render the 'view' template         |
+---------------------------------------------------------------+
```


```
outes/base/crud_factory.py - Our new utility functions would replace this
routes/blueprint_factory.py - No longer needed with our approach
routes/web/crud/components/generic_crud_routes.py - Redundant with our new utilities
Potentially some of the individual component files in routes/web/crud/components/ (create.py, edit.py, view.py, index.py) - depends on how specialized they are

2. Recommended structure:
Given the complexity of your application, I'd recommend:
Copyroutes/
├── base/
│   ├── route_utils.py         # Our new utility functions
│   └── components/            # Keep specialized components
├── web/
│   ├── companies.py           # All company routes (including CRUD)
│   ├── contacts.py            # All contact routes
│   ├── tasks.py               # All task routes
│   ├── opportunities.py       # All opportunity routes
│   └── ...                    # Other entity routes
└── api/                       # Keep your API structure
This simplifies your structure by:

Consolidating entity routes: Keep all routes for a single entity in one file (instead of separate CRUD files)
Using utility functions: Replace factories and generic components with our flexible utility functions
Maintaining separation: Still keep entities separate from each other and web routes separate from API routes```


add 'reports' tab - report on what tools and technologies companies are using
add 'explore' tab - used for applying different filters to draw diagrams based on technologies etc
add 'admin' tab to view db/table entries
```

# New API Srtucture

```
Would app/routes/base/route_utils.py be used for API routes as well? Or should we have a separate file file for it? Or is there no point


Concluded API routes need separate utility file for clarity.
5s






Great question! I recommend creating a separate utility file for API routes for these reasons:

Different patterns: API routes follow REST conventions and return JSON responses rather than rendering templates
Different error handling: API routes return status codes rather than Flash messages or redirects
Different request/response cycles: APIs don't need template rendering, form handling, etc.
I'd suggest:

routes/
├── base/
│   ├── route_utils.py         # Web route utilities (HTML templates, redirects)
│   └── api_utils.py           # API route utilities (JSON responses, status codes)
Here's what api_utils.py might focus on:

Standard CRUD operations returning JSON
Consistent error response format
Authorization handling
Input validation for API requests
Each file would focus on its specific domain:

route_utils.py for page rendering, redirects, and session-based interactions
api_utils.py for structured data exchange and REST conventions
This separation maintains the DRY principle within each context while acknowledging the fundamental differences between web and API routes.
```
----

replace - ctx.model.__tablename__ - with one of the lookup funcs

replace _table.html with _table_template.html


resources.py  - /data

----

Run tests:
```

```

```
I currently have user-to-user mappings working. I now want to add mappings for user-to-companies, user-to-opportunities, user-to-contacts, contacts-to-contacts, contacts-to-opportunities, and opportunities-to-companies.

Here's my tree. I want this to be as DRY as possible and use existing code and patterns where possible. Give me a succinct overview of how we're going to achieve this. then tell me which file(s) you need to get started. Give me one step at a time, then stop and ask if I have questions.

.
├── README.md
├── README_FOR_TESTING.md
├── add_page.py
├── app
│   ├── __init__.py
│   ├── app.py
│   ├── crm.db
│   ├── flask_session
│   │   └── 2029240f6d1128be89ddc32729463129
│   ├── models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── capability.py
│   │   ├── capability_category.py
│   │   ├── company.py
│   │   ├── company_capability.py
│   │   ├── contact.py
│   │   ├── crisp_score.py
│   │   ├── mixins.py
│   │   ├── note.py
│   │   ├── opportunity.py
│   │   ├── relationship.py
│   │   ├── table_config.py
│   │   ├── task.py
│   │   └── user.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── generic.py
│   │   │   ├── opportunities.py
│   │   │   ├── search.py
│   │   │   ├── table_config.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   ├── base
│   │   │   ├── __init__.py
│   │   │   ├── components
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_route_handler.py
│   │   │   │   ├── form_handler.py
│   │   │   │   ├── item_manager.py
│   │   │   │   ├── json_validator.py
│   │   │   │   ├── request_logger.py
│   │   │   │   ├── table_config_manager.py
│   │   │   │   └── template_renderer.py
│   │   │   └── crud_base.py
│   │   ├── router.py
│   │   ├── ui
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── opportunities.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   ├── web
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── crisp_score.py
│   │   │   ├── generic.py
│   │   │   ├── main.py
│   │   │   ├── opportunities.py
│   │   │   ├── relationship.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   └── web.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── company_capability_service.py
│   │   ├── crud_service.py
│   │   ├── mention.py
│   │   ├── relationship_service.py
│   │   ├── user_service.py
│   │   └── validator_mixin.py
│   ├── static
│   │   ├── css
│   │   │   ├── autoComplete.css
│   │   │   ├── avatar.css
│   │   │   ├── dropdown.css
│   │   │   ├── main.css
│   │   │   ├── navbar.css
│   │   │   ├── style.css
│   │   │   └── table.css
│   │   └── js
│   │       ├── pages
│   │       └── table
│   └── templates
│       ├── base
│       │   ├── common
│       │   └── errors
│       ├── components
│       ├── create_view_edit
│       │   └── components
│       ├── entity_tables
│       ├── macros
│       │   └── form_fields
│       └── relationship
├── config.py
├── create_admin.py
├── create_db.py
├── crm.db
├── detailed_test_report_20250331_130405.log
├── flask_session
│   └── 2029240f6d1128be89ddc32729463129
├── htmlcov
│   ├── favicon_32_cb_58284776.png
│   ├── keybd_closed_cb_ce680311.png
│   ├── status.json
│   └── style_cb_8e611ae1.css
├── migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 40adf23510af_initial_migration.py
├── mypy_report
│   └── index.txt
├── pyproject.toml
├── requirements.txt
├── run_checks.sh
├── test_details.log
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── conftest_skip.py
    ├── fixtures
    │   ├── __init__.py
    │   └── mock_data.py
    ├── functional
    │   ├── __init__.py
    │   ├── test_auth_flow.py
    │   ├── test_auth_flow_simple.py
    │   └── test_mock_auth.py
    ├── mark_db_tests.py
    ├── skip_db_tests.py
    └── unit
        ├── __init__.py
        ├── models
        │   ├── __init__.py
        │   └── test_user_model.py
        ├── test_auth_additional.py
        ├── test_auth_basic.py
        ├── test_auth_routes.py
        ├── test_basic.py
        ├── test_login_redirect.py
        └── test_login_view.py

36 directories, 114 files

```

# Instructions
To achieve the mappings you've described (user-to-companies, user-to-opportunities, user-to-contacts, contacts-to-contacts, contacts-to-opportunities, opportunities-to-companies), we will:

Reuse Existing Relationships: The relationship.py file already seems to be handling relationships between entities. We'll extend it by adding the new mappings between users, companies, opportunities, and contacts.

Extend Model Classes: We'll modify the existing user.py, contact.py, company.py, and opportunity.py model classes to include the necessary relationships, ensuring they stay DRY by following existing patterns.

Update Services: We'll modify or add services (e.g., user_service.py, relationship_service.py) to manage these relationships programmatically. We'll also ensure that the data flow through the system stays consistent and efficient.

Handle Routes: We'll need to add appropriate API routes in users.py, companies.py, contacts.py, and opportunities.py to allow interactions with these new relationships via the frontend.

Template Updates: We will extend existing templates in company.py, contact.py, and opportunity.py to display or interact with the new relationships.

File(s) needed to get started:
models/relationship.py — We’ll likely need to extend this for the new mappings.

models/user.py, models/contact.py, models/company.py, models/opportunity.py — To modify models and add relationships.

services/relationship_service.py — If we need to create or fetch any new relationships.

routes/api/users.py, routes/api/companies.py, routes/api/contacts.py, routes/api/opportunities.py — For the API endpoints related to these relationships.

Let's start with the first step: extending the relationship.py model to include these new mappings.

Do you have any questions before we move forward?

----

navbar:
EoQ m, w, d - Target %
EoY m, w, d - Target %


add 'relationships' tab - it'll show diagrams

I want to be able to edit individual fields without having to edit whole form (pencil icon)
create form compeltely broken
linked contacts do not show email address in brackets
add 'associates' field to map friendships/contacts outside of the business - they should be stored as regular 'contacts' too and draw 6 degree of separation diagrams to/from them between businesses and internal employees

forecast Q
user profile
update feed/notificaiton box for each notable change

edit history in admin view

synergy grpahs, node sizes, etc - varying lebel of detailed graphs of fliterable and group by graps

----

will.AI.m

questions, reminders, tips, challenging, and suggestions such as:
why haven't you spoken to the champion in the last 3 weeks?
why is it taking to long to get to PoC?
are you sure there's no compeittors?


include stats and links to articles and facts that help emphasise the importance of what needs to get done and by when

adapts to the person's personality type based on their responses and asks feedback from them in terms of how it can deliver the information more helpfully

advise that manager can see the responses - manager can

users can thumbs up, love and thumbs down feedback from ai - thumbs up is good feedback for the system, love is something we need to spend time on improving furhter, thumbs down is something that we need to seriously investigate


----
analyse notes

have a an 'analyse' or 'review' button that an SE can click - that then chats to the SE about:
* confirmation on whether x, y, z technology are being used, and if they are, add them to the approrpriate secitons - add competitors, etc
* if their ntoes conlict late,r bring it ot their attention or give them insights that on x date you said y and then there's z
* analyse ntoes for things like 'a few weeks' and ask if they want a reminder in a few weeks

----

give suggested next meeting agenda, call to action, suggest who to reach out to internally, past customers, etcs

automation off the back of notes put in:
discovery questions
open ended questions
meddpicc progress - and advice on how to achieve further progress, what are teh gaps and why

add a 'shortcut' button/ready to PoV button that helps the SE gather the remaining things needed to move forward for the pov - at the end, critique it and ask if they're sure they're satisfied with their responses?

generate a Success Criteria document off the back of all of the info that has been provided


-----

all of the above will also provide an always up to date, succinct 'exec summary'

----

diagrams & graps:
showing who owns which relationship (who owns the EB relationship)
which customers have used the same technologies
which colleagues owned those accounts
linkedin connections to target customer

crisp score
SE confidence level on the win/tech win
SEs don't have to be the bad guy, and I don't have to waste my time - if the metrics aren't there, they're not there


timeline view that shows time between updates and the growth of the opportunity over time - as well as the AI's feedback


-----

none of this is about duplicating work. all of this is about accelerating your success
