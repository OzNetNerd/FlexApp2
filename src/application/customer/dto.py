class CustomerDTO:
    def from_entity(customer: 'Customer') -> 'CustomerDTO':
        """
        Converts a Customer domain entity to a CustomerDTO.

        Args:
            customer: The customer domain entity

        Returns:
            CustomerDTO: Data transfer object with customer data
        """
        # Implementation would map entity properties to DTO
        return CustomerDTO(
            id=customer.id,
            name=customer.name,
            email=customer.email.value,
            # Other relevant properties
        )


class CreateCustomerDTO:
    def __init__(self, name: str, email: str, phone: str = None, address: str = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address


class UpdateCustomerDTO:
    def __init__(self, id: str, name: str = None, email: str = None, phone: str = None, address: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address