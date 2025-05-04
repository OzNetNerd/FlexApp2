#!/bin/bash

# Create base directory structure
mkdir -p app/graphql/types
mkdir -p app/graphql/resolvers
mkdir -p app/graphql/dataloaders

# Create empty __init__.py files
touch app/graphql/__init__.py
touch app/graphql/types/__init__.py
touch app/graphql/resolvers/__init__.py
touch app/graphql/dataloaders/__init__.py

# Create empty schema.py file
touch app/graphql/schema.py

# Create empty type files for root models
touch app/graphql/types/capability.py
touch app/graphql/types/capability_category.py
touch app/graphql/types/company_capability.py

# Create empty type files for page models
touch app/graphql/types/company.py
touch app/graphql/types/contact.py
touch app/graphql/types/crisp.py
touch app/graphql/types/note.py
touch app/graphql/types/opportunity.py
touch app/graphql/types/setting.py
touch app/graphql/types/srs.py
touch app/graphql/types/task.py
touch app/graphql/types/user.py

# Create empty resolver files
touch app/graphql/resolvers/capability.py
touch app/graphql/resolvers/capability_category.py
touch app/graphql/resolvers/company_capability.py
touch app/graphql/resolvers/company.py
touch app/graphql/resolvers/contact.py
touch app/graphql/resolvers/crisp.py
touch app/graphql/resolvers/note.py
touch app/graphql/resolvers/opportunity.py
touch app/graphql/resolvers/setting.py
touch app/graphql/resolvers/srs.py
touch app/graphql/resolvers/task.py
touch app/graphql/resolvers/user.py

# Create empty dataloader files
touch app/graphql/dataloaders/loaders.py

echo "GraphQL directory structure created successfully!"
