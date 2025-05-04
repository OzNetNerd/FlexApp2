# app/graphql/schema.py
import strawberry
from app.graphql.resolvers.user import UserQueries, UserMutations
# Import other resolvers as needed

@strawberry.type
class Query(UserQueries):
    pass

@strawberry.type
class Mutation(UserMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)