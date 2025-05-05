# src/application/opportunity/commands.py
class OpportunityCommandHandler:
    def __init__(self, opportunity_repository, unit_of_work):
        self.repository = opportunity_repository
        self.unit_of_work = unit_of_work

    def handle_create_opportunity(self, command: 'CreateOpportunityDTO') -> str:
        """Creates a new opportunity from the provided data"""
        with self.unit_of_work:
            opportunity = self.repository.create_from_dto(command)
            self.unit_of_work.commit()
            return opportunity.id

    def handle_update_opportunity(self, command: 'UpdateOpportunityDTO') -> None:
        """Updates an existing opportunity with the provided data"""
        with self.unit_of_work:
            opportunity = self.repository.find_by_id(command.id)
            opportunity.update_from_dto(command)
            self.repository.save(opportunity)
            self.unit_of_work.commit()