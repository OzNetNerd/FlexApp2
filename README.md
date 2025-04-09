# Research
Defensive programming?


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
|  Returns context object (EntityContext or TableContext)        |
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

finish this - from app.utils.table_helpers import get_table_id_by_name

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
│   ├── __init__.py
│   ├── app.py
│   ├── crm.db
│   ├── flask_session
│   │   └── 2029240f6d1128be89ddc32729463129
│   ├── models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── capability.py
│   │   ├── capability_category.py
│   │   ├── company.py
│   │   ├── company_capability.py
│   │   ├── contact.py
│   │   ├── crisp_score.py
│   │   ├── mixins.py
│   │   ├── note.py
│   │   ├── opportunity.py
│   │   ├── relationship.py
│   │   ├── table_config.py
│   │   ├── task.py
│   │   └── user.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── generic.py
│   │   │   ├── opportunities.py
│   │   │   ├── search.py
│   │   │   ├── table_config.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   ├── base
│   │   │   ├── __init__.py
│   │   │   ├── components
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_route_handler.py
│   │   │   │   ├── form_handler.py
│   │   │   │   ├── item_manager.py
│   │   │   │   ├── json_validator.py
│   │   │   │   ├── request_logger.py
│   │   │   │   ├── table_config_manager.py
│   │   │   │   └── template_renderer.py
│   │   │   └── crud_base.py
│   │   ├── router.py
│   │   ├── ui
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── opportunities.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   ├── web
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── crisp_score.py
│   │   │   ├── generic.py
│   │   │   ├── main.py
│   │   │   ├── opportunities.py
│   │   │   ├── relationship.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   └── web.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── company_capability_service.py
│   │   ├── crud_service.py
│   │   ├── mention.py
│   │   ├── relationship_service.py
│   │   ├── user_service.py
│   │   └── validator_mixin.py
│   ├── static
│   │   ├── css
│   │   │   ├── autoComplete.css
│   │   │   ├── avatar.css
│   │   │   ├── dropdown.css
│   │   │   ├── main.css
│   │   │   ├── navbar.css
│   │   │   ├── style.css
│   │   │   └── table.css
│   │   └── js
│   │       ├── pages
│   │       └── table
│   └── templates
│       ├── base
│       │   ├── common
│       │   └── errors
│       ├── components
│       ├── create_view_edit
│       │   └── components
│       ├── entity_tables
│       ├── macros
│       │   └── form_fields
│       └── relationship
├── config.py
├── create_admin.py
├── create_db.py
├── crm.db
├── detailed_test_report_20250331_130405.log
├── flask_session
│   └── 2029240f6d1128be89ddc32729463129
├── htmlcov
│   ├── favicon_32_cb_58284776.png
│   ├── keybd_closed_cb_ce680311.png
│   ├── status.json
│   └── style_cb_8e611ae1.css
├── migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 40adf23510af_initial_migration.py
├── mypy_report
│   └── index.txt
├── pyproject.toml
├── requirements.txt
├── run_checks.sh
├── test_details.log
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── conftest_skip.py
    ├── fixtures
    │   ├── __init__.py
    │   └── mock_data.py
    ├── functional
    │   ├── __init__.py
    │   ├── test_auth_flow.py
    │   ├── test_auth_flow_simple.py
    │   └── test_mock_auth.py
    ├── mark_db_tests.py
    ├── skip_db_tests.py
    └── unit
        ├── __init__.py
        ├── models
        │   ├── __init__.py
        │   └── test_user_model.py
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
