# Project README - Technical Overview

# Routing and Context Class Documentation

This document explains the key classes and enums used for defining routes, managing request context, and standardizing CRUD operations in the Flask CRM application.

---

## 1. `CRUDEndpoint` (Enum)

* **File:** `app/routes/web/route_registration.py` and `app/routes/api/route_registration.py`
* **Purpose:** Defines standard names for CRUD (Create, Read, Update, Delete) actions used consistently across both web and API route registration. This avoids using magic strings like "index" or "create".
* **Values:**
    * `index` / `get_all`: Represents listing multiple entities.
    * `create`: Represents the action of creating a new entity.
    * `view` / `get_by_id`: Represents viewing a single entity by its ID.
    * `edit` / `update`: Represents updating an existing entity by its ID.
    * `delete`: Represents deleting an entity by its ID.
* **Usage:** Used within the generic route registration functions (`register_crud_routes`, `register_api_crud_routes`) and their handlers (`route_handler`, `handle_api_crud_operation`) to determine which action to perform and which context/template to use.

---

## 2. Web Route Configuration & Context

These classes are primarily used by the web interface (`app/routes/web/`).

### 2.1. `CrudTemplates` (Dataclass)

* **File:** `app/routes/web/route_registration.py`
* **Purpose:** A simple container to hold the paths to the Jinja2 templates used for standard CRUD views (index, create, view, edit).
* **Attributes:**
    * `index`: Path to the list view template.
    * `create`: Path to the creation form template.
    * `view`: Path to the detail view template.
    * `edit`: Path to the editing form template.
* **Usage:** Instantiated by `default_crud_templates` based on entity name conventions. Passed within `CrudRouteConfig` to tell `route_handler` which template to render for each action.

### 2.2. `CrudRouteConfig` (Dataclass)

* **File:** `app/routes/web/route_registration.py`
* **Purpose:** Bundles all necessary information needed by `register_crud_routes` to automatically set up the standard web CRUD endpoints for an entity.
* **Attributes:**
    * `blueprint`: The Flask Blueprint instance to register routes onto.
    * `entity_table_name`: The singular, capitalized name of the entity (e.g., "Company", "Contact"). Used for deriving titles, routes, and finding the model.
    * `service`: An instance of the `CRUDService` (or a subclass like `UserService`) responsible for database operations for this entity.
    * `templates`: An instance of `CrudTemplates` specifying the template paths.
* **Usage:** An instance of this class is typically created in each entity's web route file (e.g., `app/routes/web/companies.py`) and then used by the dynamic registration process in `web_router.py`.

### 2.3. Web Context Classes (`app/routes/web/context.py`)

* **Purpose:** To gather and structure all data required by a Jinja2 template for rendering a specific web page. They separate the data-gathering logic from the route handler logic.
* **`WebContext`:**
    * The foundation class.
    * Initializes common attributes like `title`, `current_user`, `show_navbar`, `read_only`.
    * Provides a `to_dict()` method used by `render_safely` to pass data to templates.
* **`WebContext`:**
    * Inherits from `WebContext`.
    * Used for simple pages that mainly just need a title and the base attributes.
* **`TableWebContext`:**
    * Inherits from `WebContext`.
    * Specifically designed for entity list/index pages (`_table_index.html`).
    * Automatically calculates `entity_name`, `entity_title` (plural), `entity_base_route`, `api_url`, and `table_id` based on the `entity_table_name` or `model_class` provided.
    * Provides the necessary context variables for the AG Grid table setup in the template.
* **`TableWebContext`:**
    * Inherits from `WebContext`.
    * Used for pages dealing with a single entity (view, create, edit).
    * Holds the specific `entity` object (or an empty dict for 'create').
    * Stores the current `action` (e.g., 'view', 'edit').
    * Calculates the `submit_url` for forms based on the action and entity ID.
    * Can hold additional data like `autocomplete_fields` or related entities.
* **Usage:** Instantiated automatically by the `@use_context` decorator or manually within route handlers. The instance is then passed to `render_safely`.

---

## 3. API Route Configuration & Context

These classes are primarily used by the API (`app/routes/api/`).

### 3.1. `ApiCrudRouteConfig` (Dataclass)

* **File:** `app/routes/api/route_registration.py`
* **Purpose:** Similar to `CrudRouteConfig` but for API routes. Bundles information needed by `register_api_crud_routes` to set up standard RESTful endpoints.
* **Attributes:**
    * `blueprint`: The Flask Blueprint instance for API routes.
    * `entity_table_name`: The singular, capitalized name of the entity.
    * `service`: The `CRUDService` instance for the entity.
    * `include_routes`: Optional list of `CRUDEndpoint` values to include (defaults to all).
* **Usage:** An instance is created in each entity's API route file (e.g., `app/routes/api/companies.py`) and used by the dynamic registration in `api_router.py`.

### 3.2. API Context Classes (`app/routes/api/context.py`)

* **Purpose:** To structure the data returned by API handlers *before* it gets wrapped by the `@json_endpoint` decorator. Ensures consistent response formats.
* **`ApiContext`:**
    * Base class, primarily for shared initialization logic.
* **`ListApiContext`:**
    * Used for endpoints returning multiple items (e.g., `GET /api/companies`).
    * Structures the response with a `data` key containing the list of items (converted to dictionaries via their `to_dict()` method) and a `meta` key containing total count, entity type, and optional pagination info.
* **`EntityApiContext`:**
    * Used for endpoints returning a single item (e.g., `GET /api/companies/1`, `POST /api/companies`).
    * Structures the response with a `data` key containing the single entity's dictionary representation and a `meta` key with the entity type. Can also include a success `message`.
* **`ErrorApiContext`:**
    * Used to structure error responses.
    * Contains `message`, `status_code`, optional `error_code`, and optional `field_errors`.
    * Its `to_dict()` method creates the dictionary that `@json_endpoint` wraps within the `"error"` key of the final JSON response.
* **Usage:** Instantiated within `handle_api_crud_operation` based on the operation performed and its outcome. The resulting context object is returned to the `@json_endpoint` decorator for final formatting and serialization.

---

This structure promotes consistency and reduces repetition by:
1.  Using Enums for standard action names.
2.  Using Dataclasses to configure route generation.
3.  Using generic handlers (`route_handler`, `handle_api_crud_operation`) driven by configuration.
4.  Using Context objects to decouple data gathering/structuring from route logic and template rendering/JSON serialization.
5.  Using Decorators (`@use_context`, `@json_endpoint`) to abstract away common pre-processing and post-processing tasks.


---

# Detailed Routing, Context, and Rendering Flow

This section expands on how user requests are handled, from matching a URL to rendering a template or returning an API response. It focuses on the interplay between Blueprints, route registration, context objects, and the rendering pipeline.

## 1. Blueprints: Organizing the Application

* **Purpose:** Blueprints are Flask's way of organizing an application into distinct components. Instead of defining all routes in one large `app.py`, you group related routes together.
* **Structure:** Your app uses blueprints primarily based on entities (e.g., `companies_bp`, `contacts_bp`, `users_bp`) and separates concerns between the web UI (`app/routes/web/`) and the API (`app/routes/api/`).
* **Benefits:**
    * **Modularity:** Makes the codebase easier to navigate and maintain.
    * **Reusability:** Blueprints could potentially be reused in other projects.
    * **URL Prefixes:** Each blueprint defines a base URL prefix (e.g., `/companies`, `/api/contacts`), keeping URLs consistent for related functionalities.

## 2. Dynamic Registration: Automating Setup

* **Problem:** Manually importing and registering every single blueprint in `app.py` can become tedious and error-prone as the application grows.
* **Solution:** Your application uses helper functions (`app/routes/web_router.py`, `app/routes/api_router.py`) that leverage a utility like `register_blueprint_routes` (likely found in `app/utils/router_utils.py`).
* **Mechanism:**
    1.  The `register_blueprint_routes` function probably scans the specified package path (e.g., `app.routes.web`).
    2.  It looks for Python files and imports them.
    3.  Within each file, it searches for variables matching a specific convention (e.g., ending in `_bp` for blueprint instances or `_crud_config` / `_api_crud_config` for configuration objects).
    4.  It then calls the appropriate registration function (`register_crud_routes` for web, `register_api_crud_routes` for API, or `app.register_blueprint` directly) for each discovered item.
* **Benefit:** New entities or sections with standard routes can be added just by creating the necessary blueprint file and configuration object; the routers automatically pick them up without needing changes in `app.py`.

## 3. CRUD Route Registration: Standardizing Common Routes

* **Problem:** Defining the standard index, create, view, edit, and delete routes for every entity involves repetitive code.
* **Solution:** Generic registration functions (`register_crud_routes` for web, `register_api_crud_routes` for API) automate this.
* **Mechanism (Web - `app/routes/web/route_registration.py`):**
    1.  `register_crud_routes` receives a `CrudRouteConfig` dataclass instance. This config bundles the blueprint, the entity's name (e.g., "Company"), the specific `CRUDService` instance for that entity, and the paths to the Jinja templates (`CrudTemplates`).
    2.  It defines URL rules for standard actions (e.g., `GET /`, `GET /new`, `POST /new`, `GET /<int:entity_id>`, etc.).
    3.  Crucially, it maps *all* these standard web routes to a single, generic `route_handler` function.
    4.  This `route_handler` uses the `endpoint` name (like 'index', 'view', 'create') passed to it during registration to determine the current action.
    5.  For POST requests (create, edit, delete), it calls `handle_crud_operation`, which executes the corresponding service method (e.g., `service.create(form_data)`) and returns a `redirect`.
    6.  For GET requests, it determines the appropriate context class (`TableWebContext` for 'index', `TableWebContext` for 'view'/'edit'/'create') and template path.
    7.  It wraps the generated handler with `@login_required` to enforce authentication.
* **Mechanism (API - `app/routes/api/route_registration.py`):**
    1.  `register_api_crud_routes` receives an `ApiCrudRouteConfig`.
    2.  It defines URL rules for standard RESTful actions (e.g., `GET /`, `POST /`, `GET /<id>`, `PUT /<id>`, `DELETE /<id>`).
    3.  It maps these routes to specific internal functions (like `func_get_all`, `func_create`) generated by `make_func`.
    4.  These internal functions all call `handle_api_crud_operation`, passing the action type (e.g., 'get_all'), service, entity name, ID (if applicable), and request data.
    5.  `handle_api_crud_operation` performs the service call and wraps the result in an appropriate API Context object (`ListApiContext`, `EntityApiContext`, `ErrorApiContext`).
    6.  All generated API handlers are wrapped with the `@json_endpoint` decorator.

## 4. Context Injection (Web - `@use_context`)

* **Problem:** View functions often need to fetch data (like the specific entity being viewed) before they can even start processing the request logic. Doing this fetching directly inside *every* view function is repetitive and mixes concerns.
* **Solution:** The `@use_context` decorator (`app/routes/web/context_utils.py`) acts as middleware for your view functions.
* **Mechanism:**
    1.  You decorate your route handler (e.g., `def view(context, entity_id):`) with `@use_context(TableWebContext, entity_table_name="Company", action="view")`.
    2.  When a request hits the route, Flask calls the decorator *before* your `view` function.
    3.  The decorator inspects its arguments (`TableWebContext`, `entity_table_name`, `action`).
    4.  It identifies that it needs an entity (because it's using `TableWebContext` and the action is 'view' or 'edit').
    5.  It extracts the `entity_id` from the URL kwargs.
    6.  It uses the `entity_table_name` to look up the correct model (via `get_model_by_name`) and instantiates the corresponding `CRUDService`.
    7.  It calls `service.get_by_id(entity_id)` to fetch the data.
    8.  It instantiates `TableWebContext`, passing the fetched entity, the action ('view'), and other necessary details.
    9.  Finally, it calls your original `view` function, injecting the fully prepared `context` object as a keyword argument.
* **Benefit:** Your view function receives a ready-to-use `context` object containing all necessary data, making the view code much cleaner and focused on request handling or template rendering.

## 5. Context Objects (`app/routes/web/context.py`, `app/routes/api/context.py`)

* **Purpose:** These classes act as structured containers for data needed either by templates (web) or for JSON serialization (API).
* **Web Context (`TableWebContext`, `TableWebContext`):**
    * Gather data like the page title, the main entity/entities being displayed, related data (e.g., notes, relationships fetched via service calls or model properties), the current user, configuration flags (`read_only`), and URLs needed for links/forms (`submit_url`).
    * The `to_dict()` method prepares this data for passing to `render_template`.
    * `TableWebContext` is specialized for list views (index pages), setting up data needed by `_table_index.html` (like `api_url`, `table_id`).
    * `TableWebContext` is for single-item views/forms, holding the specific `entity` object and action type.
* **API Context (`ListApiContext`, `EntityApiContext`, `ErrorApiContext`):**
    * Primarily used to structure the data *before* it's passed to `@json_endpoint`.
    * `ListApiContext`: Wraps lists of results, adding metadata like total counts and pagination info if applicable.
    * `EntityApiContext`: Wraps a single entity result.
    * `ErrorApiContext`: Structures error responses with a message, status code, and optional field errors.
    * Their `to_dict()` methods produce the dictionary structure that `@json_endpoint` will wrap in the final `{"success": ..., "data": ...}` or `{"success": ..., "error": ...}` response.

## 6. Rendering & Response Generation

* **Web (`render_safely` in `app/routes/web/components/template_renderer.py`):**
    * This is a robust wrapper around Flask's `render_template`.
    * **Context Handling:** Takes the `context` object, calls `context.to_dict()`, and passes the resulting dictionary to the template.
    * **Error Detection:** Uses a custom Jinja environment with `LoggingUndefined`. If a template tries to access a variable not present in the context dictionary (e.g., `{{ non_existent_var }}`), `LoggingUndefined` logs a warning *instead* of crashing the render immediately (during development). It tracks these missing variables.
    * **Global Injection:** Ensures Flask globals (`url_for`, `request`, `current_user`, etc.) are available within the template.
    * **Post-Render Check:** After rendering, it checks if any undefined variables were logged by `LoggingUndefined`. If so, it raises an error (in development) to force developers to fix missing context data.
    * **Exception Handling:** Catches `TemplateNotFound` (leading to a 404) and other Jinja/Python exceptions during rendering, logging them and potentially rendering a user-friendly 500 error page.
* **API (`@json_endpoint` in `app/routes/api/json_utils.py`):**
    * This decorator standardizes all API output.
    * **Success Path:** It takes the return value from the API handler (which might be raw data or an API Context object). If it's a context object, it calls `to_dict()`. It then wraps this data in `{"success": True, "data": data}` and uses `jsonify` to create the Flask response with a 200 status (or the status provided by the handler).
    * **Error Path:** If the handler raises an `HTTPException` or any other `Exception`, the decorator catches it. It creates an `ErrorApiContext` (or uses the one returned by `handle_api_crud_operation`), calls `to_dict()`, wraps it in `{"success": False, "error": error_data}`, and returns the `jsonify` response with the appropriate error status code (e.g., 404, 500).

This detailed flow shows a highly structured and automated approach to handling requests, managing data context, and generating responses, aiming for consistency and reduced boilerplate across both the web and API layers.


-----

## 1. Project Overview

This document provides a technical overview of the Flask-based CRM application. It details the architecture, key components, and how different parts of the application are connected, including the database layer, routing, services, frontend JavaScript, and decorator usage. The application aims to provide a robust platform for managing companies, contacts, opportunities, tasks, and related interactions.

## 2. Technology Stack

* **Backend:** Python 3.x, Flask
* **Database:** SQLAlchemy (ORM), Flask-Migrate (Migrations), SQLite (default, configurable via `DATABASE_URL` env var)
* **Templating:** Jinja2
* **Frontend:** HTML5, CSS3 (Bootstrap 5, Custom CSS), JavaScript (ES Modules)
* **Authentication:** Flask-Login
* **Testing:** Pytest, Coverage.py
* **Code Quality & Linting:** Black, isort, Flake8, Mypy, Bandit, Safety, Pydocstyle, Detect-Secrets, pre-commit

## 3. Project Structure

The application follows a modular structure within the `app/` directory:

app/
├── models/             # SQLAlchemy ORM models (e.g., User, Company, Contact)
│   ├── base.py         # BaseModel with common methods (save, delete, to_dict)
│   ├── relationship.py # Polymorphic relationship model
│   └── ...             # Individual entity models
├── routes/             # Flask blueprints and route definitions
│   ├── api/            # API specific routes (e.g., /api/companies)
│   │   ├── context.py  # API context classes (ListApiContext, etc.)
│   │   ├── json_utils.py # @json_endpoint decorator
│   │   └── route_registration.py # API CRUD route registration logic
│   ├── web/            # Web UI routes (e.g., /companies)
│   │   ├── components/ # Reusable web components (validators, renderers)
│   │   ├── context.py  # Web context classes (TableWebContext, TableWebContext)
│   │   ├── context_utils.py # @use_context decorator
│   │   └── route_registration.py # Web CRUD route registration logic
│   ├── api_router.py   # Registers all API blueprints
│   └── web_router.py   # Registers all Web blueprints
├── services/           # Business logic and data access layer
│   ├── crud_service.py # Generic CRUD service
│   └── ...             # Specialized services (Auth, User, Note, SRS, etc.)
├── static/             # CSS, JavaScript, images
│   ├── css/            # New CSS structure (main.css imports others)
│   ├── js/             # New JavaScript structure (modules)
│   │   ├── core/       # Core JS modules (logger, module system, events)
│   │   ├── components/ # Reusable JS components (table, notes, form, etc.)
│   │   ├── pages/      # Page-specific JS logic (common, entityList, etc.)
│   │   └── services/   # Frontend services (apiService, uiService, etc.)
│   ├── css_old/        # Older CSS assets (potentially deprecated)
│   └── js_old/         # Older JS assets (potentially deprecated)
├── templates/          # Jinja2 templates (new structure)
│   ├── layouts/        # Base layout templates (base.html, _table_index.html)
│   ├── pages/          # Page-specific templates (e.g., companies/index.html)
│   ├── partials/       # Reusable template snippets (navbar.html, notes.html)
│   └── macros/         # Reusable Jinja2 macros (fields.html, card.html)
├── templates_old/      # Older template structure (potentially deprecated)
├── utils/              # Utility functions (logging, model registry, etc.)
└── app.py              # Flask application factory and core setup

config.py             # Application configuration class
create_db.py          # Database initialization and seeding script
create_admin.py       # Script for seeding data/admin user
requirements.txt      # Python dependencies
pyproject.toml        # Build system and tool configuration (Black, isort)
.pre-commit-config.yaml # Pre-commit hook configurations
run_checks.sh         # Script for running code quality checks and tests
tests/                # Unit and functional tests

## 4. Core Components

### 4.1. Configuration (`config.py`)

* Manages application settings via a `Config` class.
* Uses environment variables (`SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG`) with sensible defaults.
* Configures Flask session parameters (type, lifetime, cookie security).
* Sets SQLAlchemy database URI, defaulting to SQLite (`crm.db`) but configurable via `DATABASE_URL`.

### 4.2. Flask Application Factory (`app/app.py`)

* Uses the `create_app` factory pattern to initialize the Flask app.
* Initializes extensions: `SQLAlchemy`, `LoginManager`, `Migrate`.
* Configures `Flask-Login`: sets the login view (`auth_bp.login`), handles user loading (`@login_manager.user_loader`), and defines the unauthorized handler.
* Sets up console logging using `app/utils/app_logging.py`.
* Registers API and Web blueprints via `register_api_blueprints` and `register_web_blueprints`.
* Includes `before_request` hooks:
    * `log_request`: Logs details of each incoming request.
    * `require_login`: Redirects unauthenticated users to the login page for protected routes (endpoints not in `whitelisted`).
* Injects global variables (`now`, `current_user`, `is_debug_mode`, etc.) into all Jinja templates via `@app.context_processor`.
* Ensures database tables are created (`db.create_all()`) and default settings are seeded (`Setting.seed()`) on startup.

### 4.3. Database Layer (`app/models/`)

* **ORM:** Leverages `SQLAlchemy` for database interactions.
* **Base Model (`app/models/base.py`):**
    * Provides common attributes (`__tablename__`, `__entity_name__`, `__entity_plural__`) derived from the class name.
    * Includes standard methods: `save()`, `delete()`, `to_dict()` for serialization.
    * Initializes instances from keyword arguments (`__init__`).
* **Models:** Defines application entities (e.g., `User`, `Company`, `Contact`, `Opportunity`, `Task`, `Note`, `Capability`, `SRS`). Each model inherits from `BaseModel`.
* **Relationships:**
    * Standard relationships (one-to-many, many-to-one) are defined using `db.relationship` with `back_populates` or `backref`.
    * **Polymorphic Notes:** The `Note` model uses `notable_type` (e.g., 'Company', 'Contact') and `notable_id` to link to different parent entities.
    * **Polymorphic Relationships (`app/models/relationship.py`):** A generic `Relationship` table links any two entities using `entity1_type`, `entity1_id`, `entity2_type`, `entity2_id`, and an optional `relationship_type` string. This allows flexible connections (e.g., User-Contact, Contact-Company, User-User). Model properties like `Contact.managers` or `User.relationships` use `primaryjoin` conditions on the `Relationship` table to fetch related entities.
* **Form Metadata (`app/models/form_metadata.py`):** Defines dynamic form structures (`FormTab`, `FormSection`, `FormField`) stored in the database. This allows configuring forms (fields, visibility, order, type) without code changes. `FormDefinition.get_form_definition` retrieves the structure for rendering.
* **Migrations:** Uses `Flask-Migrate` (evident from `migrations/` folder and `Migrate` initialization) for managing database schema evolution.
* **Initialization & Seeding (`create_db.py`, `create_admin.py`):** Scripts used to create the database schema and populate it with initial/sample data, including handling potential duplicates (`create_or_update` pattern).

### 4.4. Routing (`app/routes/`)

* **Blueprints:** Routes are organized into Flask Blueprints, separating API (`app/routes/api/`) and Web (`app/routes/web/`) concerns. Entity-specific routes are typically grouped within their respective blueprint files (e.g., `app/routes/web/companies.py`).
* **Dynamic Registration:**
    * `app/routes/web_router.py` and `app/routes/api_router.py` use `register_blueprint_routes` (from `app/utils/router_utils.py`) to automatically discover and register blueprints based on naming conventions (e.g., `_bp` suffix) and configuration objects (e.g., `_crud_config`, `_api_crud_config`).
    * This reduces boilerplate registration code in `app.py`.
* **Web CRUD Registration (`app/routes/web/route_registration.py`):**
    * `register_crud_routes` function takes a `CrudRouteConfig` (containing blueprint, entity name, service, templates) and registers standard web routes (`/`, `/new`, `/<id>`, `/<id>/edit`, `/<id>/delete`).
    * It uses a generic `route_handler` which determines the correct context (`TableWebContext` or `TableWebContext`) and template based on the endpoint (`index`, `create`, `view`, `edit`, `delete`).
    * Handles POST requests for `create`, `edit`, `delete` by calling the appropriate service method via `handle_crud_operation`.
    * All generated routes are wrapped with `@login_required`.
* **API CRUD Registration (`app/routes/api/route_registration.py`):**
    * Similar to web routes, `register_api_crud_routes` uses `ApiCrudRouteConfig` to register standard RESTful API endpoints (`GET /`, `POST /`, `GET /<id>`, `PUT /<id>`, `DELETE /<id>`).
    * Uses `handle_api_crud_operation` to call the appropriate service method based on the HTTP method and presence of an ID.
    * All handlers are wrapped with the `@json_endpoint` decorator.
* **Context Injection (`@use_context` in `app/routes/web/context_utils.py`):**
    * This decorator simplifies view functions by automatically creating and injecting the appropriate context object (`TableWebContext`, `TableWebContext`) based on the provided class and arguments.
    * It handles fetching the entity for view/edit actions and passes the context object as a `context` keyword argument to the decorated view function.
* **JSON Response Decorator (`@json_endpoint` in `app/routes/api/json_utils.py`):**
    * Wraps API view functions to ensure consistent JSON responses.
    * On success, returns `{"success": True, "data": ...}`.
    * Catches `HTTPException` and other errors, returning `{"success": False, "error": ...}` with the appropriate status code.
    * Automatically converts context objects with a `to_dict()` method into dictionaries.

### 4.5. Services Layer (`app/services/`)

* Acts as an intermediary between routes and models, containing business logic.
* **`CRUDService` (`app/services/crud_service.py`):** Provides generic `get_all` (with pagination/sorting/filtering), `get_by_id`, `create`, `update`, `delete` methods applicable to any model. It can enforce `required_fields` during creation.
* **Specialized Services:**
    * `AuthService`: Handles user login/logout logic.
    * `UserService`: Extends `CRUDService` and adds validation logic via `ValidatorMixin`.
    * `NoteService`: Extends `CRUDService` for notes, adding methods to fetch notes by related entity (`get_by_notable`) or date range.
    * `RelationshipService`: Manages the polymorphic `Relationship` model, providing methods to create, delete, and retrieve relationships between different entity types (e.g., `get_relationships_for_entity`, `get_user_companies`).
    * `SearchService`: Provides generic text search (`ilike`) across specified fields for a given model, also supporting exact filters.
    * `SRSService`: Manages `SRS` entities, interacting with the `fsrs` library (likely for spaced repetition scheduling) via methods like `schedule_review` and `preview_ratings`. It also records review history.
* **Validation (`app/services/validator_mixin.py`):** A mixin class providing `validate_create` and `validate_update` methods that can be implemented by specific services (like `UserService`) to enforce custom validation rules before creating or updating entities.

### 4.6. Templating (`app/templates/`)

* **Engine:** Uses `Jinja2`.
* **Structure:** Organizes templates into `layouts`, `pages`, `partials`, and `macros`. The `templates_old` directory suggests a refactoring or migration occurred.
* **Base Layout (`layouts/base.html`):** Defines the main HTML structure, includes head content (`_head.html`), navbar (`partials/navbar.html`), toast notifications (`_toasts.html`), and common scripts. Uses blocks (`{% block %}`) for content injection.
* **Table Index Layout (`layouts/_table_index.html`):** A specialized layout for entity listing pages, including search, filters, and the AG Grid container (`#table-container`).
* **Partials (`partials/`):** Reusable template snippets like the navbar, notes section, form components, and developer tools.
* **Macros (`macros/`):** Reusable Jinja2 functions for rendering common UI elements like form fields (`fields.html`, `render_form_fields.html`), cards (`card.html`), entity lists/tables (`entity_macros.html`), notes (`render_notes.html`), and tabs (`tabs.html`).
* **Dynamic Forms:** Templates like `entities/partials/form_field.html`, `form_section.html`, `form_tabs.html` work with the `FormDefinition` fetched from `app/models/form_metadata.py` to render forms dynamically based on database configuration.
* **Error Handling:** `render_safely` uses `LoggingUndefined` to catch undefined variables during rendering and log warnings. It also handles `TemplateNotFound` and other rendering exceptions gracefully.

### 4.7. Frontend JavaScript (`app/static/js/`)

* **Modularity:** Uses ES Modules (`import`/`export`).
* **Core (`core/`):**
    * `logger.js`: Provides a console logger with level coloring and optional file/function grouping (controlled by `nestedLoggingEnabled`).
    * `module.js`: A simple system (`ModuleSystem`) to register JS modules, manage dependencies, and control initialization order, especially concerning DOM readiness.
    * `events.js`: A basic publish/subscribe (`EventSystem`) for communication between different JS components.
    * `config.js`: (`ConfigManager`) Utility to read configuration from HTML `data-*` attributes.
    * `utils.js`: General utility functions, including `fetchApiData` (with caching).
* **Components (`components/`):** Reusable UI widgets.
    * `table.js`: Initializes and manages the AG Grid table, including fetching data, generating columns, setting up search/filtering, column selection, and saving/restoring column state via localStorage. It integrates functionalities previously in `tableConfig.js`, `tableInit.js`, `tableUtils.js`.
    * `autoComplete.js`: Implements autocomplete functionality for input fields, fetching suggestions from a specified API endpoint and managing selected items as badges.
    * `notes.js`: Manages the notes section, including loading, rendering, filtering, searching, and adding new notes via API calls.
    * `form.js`: (`FormManager`) Handles form state tracking (detecting changes), validation (HTML5 + custom), and submission logic, including unsaved changes warnings.
    * `modal.js`: (`ModalManager`) Creates and manages Bootstrap modals programmatically, including confirmation modals (like delete confirmation).
    * `tabs.js`: Manages Bootstrap tab navigation, allowing programmatic switching and state management.
    * `buttons.js`: Initializes and manages event listeners for header and footer buttons, including delete confirmation logic.
* **Pages (`pages/`):** Contains JavaScript specific to certain page types or sections.
    * `common.js`: Initializes functionality common to most pages (global event listeners, Bootstrap tooltips/popovers, debug logging setup).
    * `entityList.js`: Logic for entity listing pages, primarily initializing the data table (`table.js`) and potentially other list-specific features like highlights animation.
    * `entityView.js`: Logic for entity detail view pages, initializing components like header buttons (`buttons.js`) and the notes section (`notes.js`).
    * `notesSection.js`: (Likely refactored into `notes.js`) Specific logic for the notes partial.
    * `create_view_edit.js`, `edit.js`, `footer_buttons.js`, `header_buttons.js`: Older page-specific scripts, potentially refactored into newer component/page modules.
* **Services (`services/`):** Frontend equivalents of backend services.
    * `apiService.js`: Centralized service for making `fetch` requests to the backend API (GET, POST, PUT, DELETE, file uploads), including base URL handling and default headers.
    * `uiService.js`: Provides common UI interactions like showing loading indicators, disabling forms, and displaying toast messages (using its own simple implementation or potentially Bootstrap toasts).
    * `notificationService.js`: Listens for various application events (API errors, form validation failures, etc.) and uses `uiService` to display appropriate error/success/warning notifications (toasts).
* **Initialization (`main.js`):** The main entry point. Initializes the core logger, detects the page type based on the URL, and loads the relevant page-specific modules using the `moduleSystem`.

### 4.8. Authentication (`app/services/auth.py`, `app/routes/web/auth.py`, Flask-Login)

* Uses `Flask-Login` for session-based user authentication.
* `User` model implements `UserMixin`.
* `AuthService` handles the core login (`handle_login`) and logout (`handle_logout`) logic, including password checking (`check_password_hash`) and session management (`login_user`, `logout_user`).
* `auth_bp` blueprint defines the `/auth/login` (GET, POST) and `/auth/logout` (GET) routes.
* `@login_manager.user_loader` in `app.py` retrieves the user object from the session ID.
* `@login_manager.unauthorized_handler` redirects users to the login page if they try to access protected resources without being logged in.
* The `require_login` `before_request` hook enforces authentication globally, redirecting to login if necessary.

## 5. Key Features & Patterns

* **Application Factory:** (`app.py`) Standard Flask pattern for creating configurable app instances.
* **Blueprints:** (`app/routes/`) Modular organization of routes.
* **Service Layer:** (`app/services/`) Separates business logic from route handlers and database models.
* **Generic CRUD:** (`CRUDService`, CRUD route registration utilities) Reduces boilerplate for common data operations and route definitions.
* **Polymorphic Relationships:** (`Relationship` model, `Note` model) Allows flexible linking between different types of entities.
* **Context Injection:** (`@use_context`, `WebContext`, `TableWebContext`, `TableWebContext`) Standardizes data passing from routes to web templates.
* **API Standardization:** (`@json_endpoint`, API Context classes) Ensures consistent JSON responses and error handling for APIs.
* **Frontend Modularity:** (ES Modules, `ModuleSystem`, `EventSystem`, Components, Services) Organizes frontend code for better maintainability and reusability.
* **Dynamic Form Generation:** (`FormDefinition`, `FormTab`, etc.) Allows UI form structure to be configured via the database.
* **Spaced Repetition System (SRS):** (`SRS`, `SRSService`) Implements learning/review logic using the FSRS algorithm.
* **Comprehensive Testing & Linting:** (Pytest, Coverage, Black, Flake8, Mypy, pre-commit) Ensures code quality and reliability.

## 6. Setup & Running

1.  **Environment:** Set up a Python virtual environment.
2.  **Dependencies:** Install required packages: `pip install -r requirements.txt`. For development, also install dev dependencies: `pip install -r requirements-dev.txt`.
3.  **Configuration:** Set environment variables if needed (e.g., `DATABASE_URL`, `SECRET_KEY`, `FLASK_DEBUG=1`).
4.  **Database Setup:** Run `python create_db.py` to create the database schema. This might also seed initial data if `FLASK_DEBUG` is set. Run `python create_admin.py` if necessary for specific seeding.
5.  **Database Migrations:** If the schema changes, use Flask-Migrate commands: `flask db migrate -m "Description"` and `flask db upgrade`.
6.  **Run Development Server:** `flask --app app.app run --debug`
7.  **Run Checks:** Execute `sh run_checks.sh` to run tests, coverage reports, and linters. Install pre-commit hooks with `pre-commit install`.
