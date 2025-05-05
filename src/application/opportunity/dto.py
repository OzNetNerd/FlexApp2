# src/application/opportunity/dto.py
class CreateOpportunityDTO:
    def __init__(self, name: str, description: str = None, status: str = None,
                 value: float = None, customer_id: str = None, company_id: str = None):
        self.name = name
        self.description = description
        self.status = status
        self.value = value
        self.customer_id = customer_id
        self.company_id = company_id

class UpdateOpportunityDTO:
    def __init__(self, id: str, name: str = None, description: str = None,
                 status: str = None, value: float = None, customer_id: str = None,
                 company_id: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.value = value
        self.customer_id = customer_id
        self.company_id = company_id