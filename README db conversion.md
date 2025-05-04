# GraphQL Migration Plan
## Setup GraphQL Foundation

* Install dependencies (graphene/strawberry/ariadne)
* Create base GraphQL schema file 
* Setup single GraphQL endpoint


## Create Type System

* Define base model-to-type converter
* Auto-generate basic types from SQLAlchemy models
* Create connection between models for relationships

## Implement Query Architecture

* Define root Query type with fields for each model
* Create base resolver classes for common operations
* Move business logic from REST handlers to field resolvers

## Build Mutation System

* Implement standard mutations (create/update/delete)
* Define input types for mutation arguments
* Port validation logic from current controllers

## Migrate Special Cases

* Convert dashboard statistics to dedicated resolvers
* Implement filtering as GraphQL arguments
* Port complex operations (like user_activity_by_role)


Connect Authentication

Implement GraphQL context for auth
Port login_required decorator to GraphQL middleware
Add permission checking to resolvers


Update Frontend

Switch API calls from REST to GraphQL
Implement proper query structure with only needed fields