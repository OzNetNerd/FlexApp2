#!/bin/bash

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

echo "DDD directory structure created successfully!"
