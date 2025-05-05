# In src/application/opportunity/queries.py
class OpportunityQueryHandler:
    def __init__(self, opportunity_repository):
        self.repository = opportunity_repository

    def get_opportunity_by_id(self, opportunity_id: str) -> 'OpportunityDTO':
        """
        Retrieves an opportunity by its ID.

        Args:
            opportunity_id: The unique identifier of the opportunity

        Returns:
            OpportunityDTO: Data transfer object with opportunity data

        Raises:
            OpportunityNotFoundError: If no opportunity with the given ID exists
        """
        opportunity = self.repository.find_by_id(opportunity_id)
        return OpportunityDTO.from_entity(opportunity)