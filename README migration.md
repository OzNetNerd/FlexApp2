# Prompt

I'm migrating my app to DDD style. Review the attached file(s) and:
1. Split them up, if need be.
2. Implement improvements as you see fit. Make sure you focus on DRY.
2. Annotate the code and add informative Google style docstrings.
3. Tell me where to put the file(s).

```
# Create the main directory structure
mkdir -p src/domain/{customer,company,opportunity}/
mkdir -p src/domain/shared/{value_objects,interfaces}
mkdir -p src/application/{customer,company,opportunity}
mkdir -p src/infrastructure/{persistence/{repositories,models},auth,messaging}
mkdir -p src/interfaces/graphql/{customer,company,opportunity}
mkdir -p src/interfaces/api

# Create domain layer files
for domain in customer company opportunity; do
    touch src/domain/$domain/__init__.py
    touch src/domain/$domain/entities.py
    touch src/domain/$domain/value_objects.py
    touch src/domain/$domain/aggregates.py
    touch src/domain/$domain/repositories.py
    touch src/domain/$domain/services.py
    touch src/domain/$domain/events.py
    touch src/domain/$domain/exceptions.py
done

# Create shared domain files
touch src/domain/shared/__init__.py
touch src/domain/shared/value_objects/__init__.py
touch src/domain/shared/value_objects/email.py
touch src/domain/shared/value_objects/phone.py
touch src/domain/shared/value_objects/money.py
touch src/domain/shared/interfaces/__init__.py
touch src/domain/shared/interfaces/repository.py

# Create application layer files
for domain in customer company opportunity; do
    touch src/application/$domain/__init__.py
    touch src/application/$domain/commands.py
    touch src/application/$domain/queries.py
    touch src/application/$domain/dto.py
done
touch src/application/__init__.py

# Create infrastructure layer files
touch src/infrastructure/__init__.py
touch src/infrastructure/persistence/__init__.py
touch src/infrastructure/persistence/repositories/__init__.py
touch src/infrastructure/persistence/models/__init__.py
touch src/infrastructure/persistence/unit_of_work.py
for domain in customer company opportunity; do
    touch src/infrastructure/persistence/repositories/${domain}_repository.py
    touch src/infrastructure/persistence/models/$domain.py
done
touch src/infrastructure/auth/__init__.py
touch src/infrastructure/auth/services.py
touch src/infrastructure/messaging/__init__.py
touch src/infrastructure/messaging/event_bus.py

# Create interface layer files
touch src/interfaces/__init__.py
touch src/interfaces/graphql/__init__.py
touch src/interfaces/graphql/schema.py
for domain in customer company opportunity; do
    touch src/interfaces/graphql/$domain/__init__.py
    touch src/interfaces/graphql/$domain/types.py
    touch src/interfaces/graphql/$domain/queries.py
    touch src/interfaces/graphql/$domain/mutations.py
done
touch src/interfaces/api/__init__.py

# Create application entry point
touch src/app.py
```


Key Architectural Components
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