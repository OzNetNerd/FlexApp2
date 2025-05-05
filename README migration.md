# Prompt

I'm migrating my app to DDD style. Review the attached file(s) and:
1. Split them up, if need be.
2. Implement improvements as you see fit. Make sure you focus on DRY.
2. Annotate the code and add informative Google style docstrings.
3. Tell me where to put the file(s).

```src/
├── app.py
├── application
│   ├── __init__.py
│   ├── capability
│   │   └── dto.py
│   ├── company
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── dto.py
│   │   └── queries.py
│   ├── customer
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── dto.py
│   │   └── queries.py
│   └── opportunity
│       ├── __init__.py
│       ├── commands.py
│       ├── dto.py
│       └── queries.py
├── domain
│   ├── capability
│   │   ├── entities.py
│   │   └── repositories.py
│   ├── company
│   │   ├── __init__.py
│   │   ├── aggregates.py
│   │   ├── entities.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   └── value_objects.py
│   ├── customer
│   │   ├── __init__.py
│   │   ├── aggregates.py
│   │   ├── entities.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   └── value_objects.py
│   ├── opportunity
│   │   ├── __init__.py
│   │   ├── aggregates.py
│   │   ├── entities.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   └── value_objects.py
│   └── shared
│       ├── __init__.py
│       ├── constants.py
│       ├── entities.py
│       ├── interfaces
│       │   ├── __init__.py
│       │   ├── entity.py
│       │   └── repository.py
│       ├── services
│       │   └── relationship_service.py
│       └── value_objects
│           ├── __init__.py
│           ├── autocomplete_field.py
│           ├── email.py
│           ├── money.py
│           ├── phone.py
│           └── relationship.py
├── infrastructure
│   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── services.py
│   │   └── user_loader.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── environments.py
│   ├── context
│   │   └── base_context.py
│   ├── flask
│   │   ├── app_factory.py
│   │   ├── blueprint_factory.py
│   │   ├── error_handlers.py
│   │   ├── extensions.py
│   │   ├── middleware.py
│   │   ├── template_config.py
│   │   ├── template_renderer.py
│   │   └── template_utils.py
│   ├── logging
│   │   ├── __init__.py
│   │   └── config.py
│   ├── logging.py
│   ├── messaging
│   │   ├── __init__.py
│   │   └── event_bus.py
│   ├── persistence
│   │   ├── __init__.py
│   │   ├── config
│   │   │   └── table_config.py
│   │   ├── json_validator.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── capability.py
│   │   │   ├── company.py
│   │   │   ├── customer.py
│   │   │   ├── opportunity.py
│   │   │   ├── setting.py
│   │   │   ├── shared.py
│   │   │   └── user.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── capability_repository.py
│   │   │   ├── company_repository.py
│   │   │   ├── customer_repository.py
│   │   │   └── opportunity_repository.py
│   │   ├── seeders.py
│   │   └── unit_of_work.py
│   └── utils
│       └── router_utils.py
└── interfaces
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   └── router.py
    ├── graphql
    │   ├── __init__.py
    │   ├── company
    │   │   ├── __init__.py
    │   │   ├── mutations.py
    │   │   ├── queries.py
    │   │   └── types.py
    │   ├── customer
    │   │   ├── __init__.py
    │   │   ├── mutations.py
    │   │   ├── queries.py
    │   │   └── types.py
    │   ├── opportunity
    │   │   ├── __init__.py
    │   │   ├── mutations.py
    │   │   ├── queries.py
    │   │   └── types.py
    │   └── schema.py
    └── web
        ├── router.py
        ├── routes
        │   └── crud_routes.py
        └── views
            └── context.py

36 directories, 115 files
```

# Migration Order for Your Current Files
Here's the recommended order to migrate your existing files to the DDD structure, focusing on maintaining functionality throughout the process:

## Core Domain Models & Value Objects

models/base.py → Move to src/domain/shared/interfaces
models/mixins.py → Split into appropriate src/domain/shared components
utils/model_registry.py → Adapt for new structure in src/domain/shared


## Company Domain

models/pages/company.py → src/domain/company/entities.py
models/capability.py & models/capability_category.py → src/domain/company/value_objects.py
models/company_capability.py → src/domain/company/aggregates.py
services/crud_service.py (company parts) → src/domain/company/services.py
routes/api/companies.py → src/interfaces/api/company_controller.py


## Contact/Customer Domain

models/pages/contact.py → src/domain/customer/entities.py
routes/api/contacts.py → src/interfaces/api/customer_controller.py
services/crud_service.py (contact parts) → src/domain/customer/services.py


## Opportunity Domain

models/pages/opportunity.py → src/domain/opportunity/entities.py
models/pages/srs.py → src/domain/opportunity/entities.py (if related)
routes/api/opportunities.py → src/interfaces/api/opportunity_controller.py
services/crud_service.py (opportunity parts) → src/domain/opportunity/services.py


## Relationship Management

models/relationship.py → Create appropriate relationship models in respective domains
services/relationship_service.py → Distribute to appropriate domain services


## Infrastructure Layer

services/auth.py → src/infrastructure/auth/services.py
services/validator_mixin.py → src/infrastructure/persistence/validation.py
Create repository implementations based on your CRUD service


## Application Layer Services

services/category_service.py → src/application/company/commands.py & queries.py
services/note_service.py → Appropriate application service
services/search_service.py → src/application/shared/search_service.py
services/srs_service.py → src/application/opportunity/commands.py & queries.py
services/user_service.py → src/application/customer/commands.py & queries.py


## API Interfaces

routes/api_router.py → src/interfaces/api/__init__.py
routes/web_router.py → Adapt for new API structure
Migrate remaining route files to appropriate interface components


## App Entry Point

app.py → src/app.py (update with new imports and structure)



## Migration Approach:

1. Start with core domain models to establish your foundational building blocks 
2. Migrate one domain at a time (company → customer → opportunity) to ensure you can test each domain as you go 
3. Implement infrastructure layer as you need persistence for the domains you've migrated 
4. Build application services that coordinate between domains 
5. Update interfaces to work with the new application services 
6. Finally update the app entry point to wire everything together

This approach allows you to:

1. Maintain functionality by completing one domain before moving to the next
2. Test throughout the migration process
3. Gradually transition from your old architecture to DDD
4. Avoid having to make a "big bang" cutover that could break everything



# Key Architectural Components
1. Domain Layer
This is the core of your business logic, containing:

Entities: Business objects with identity (Customer, Company)
Value Objects: Immutable objects defined by their attributes (Email, Phone)
Aggregates: Clusters of entities and value objects treated as a unit
Domain Services: Operations that don't belong to a single entity
Repository Interfaces: Abstract interfaces for data access

2. Application Layer
This layer coordinates the application tasks:

Commands: Handle use cases that modify state (CreateCustomer, UpdateOpportunity)
Queries: Handle use cases that retrieve data
DTOs: Data Transfer Objects for moving data between layers

3. Infrastructure Layer
This handles technical concerns:

Repository Implementations: Concrete implementations of repository interfaces
ORM Models: SQLAlchemy models for database interaction
Unit of Work: Manages transactions and persistence operations
Authentication/Authorization: Infrastructure for security

4. Interface Layer
This handles user interaction:

GraphQL Schema/Resolvers: Define how clients interact with your API
REST Controllers: Alternative API if needed

Implementation Recommendations

Start with the Domain Model: Focus first on modeling your entities, value objects, and aggregates before implementing infrastructure.
Use Dependency Injection: This makes testing easier and decouples components.
GraphQL Implementation:

Define the GraphQL schema in the interfaces layer
Resolvers should delegate to application services, not directly to repositories
Consider using Strawberry or Ariadne for code-first GraphQL approaches


Repository Pattern:

Define repository interfaces in the domain layer
Implement concrete repositories in the infrastructure layer
Consider using the Unit of Work pattern for transaction management


Event-Driven Architecture:

Use domain events to decouple domains
Implement an event bus in the infrastructure layer



Migration Strategy
Since you're migrating an existing application:

Start by identifying your core domains (seems like customer, company, opportunity are already identified)
Create the new structure alongside your existing code
Begin with one bounded context (maybe start with the simplest one)
Gradually move functionality from the old structure to the new one
Run both in parallel until you've fully migrated