# src/interfaces/graphql/opportunity/types.py
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Opportunity:
    id: strawberry.ID
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    customer_id: Optional[strawberry.ID] = None
    company_id: Optional[strawberry.ID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@strawberry.input
class CreateOpportunityInput:
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    customer_id: Optional[strawberry.ID] = None
    company_id: Optional[strawberry.ID] = None

@strawberry.input
class UpdateOpportunityInput:
    id: strawberry.ID
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    customer_id: Optional[strawberry.ID] = None
    company_id: Optional[strawberry.ID] = None