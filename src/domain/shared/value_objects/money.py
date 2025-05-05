"""Money value object."""

from decimal import Decimal, ROUND_HALF_UP


class Money:
    """
    Value object representing monetary value.

    Handles currency amounts with proper decimal precision.

    Attributes:
        amount: The monetary amount as a Decimal.
        currency: Currency code (default: USD).
    """

    def __init__(self, amount, currency="USD"):
        """
        Initialize a money value.

        Args:
            amount: Numeric amount (int, float, or Decimal).
            currency: Three-letter currency code.
        """
        if isinstance(amount, str):
            self._amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            self._amount = Decimal(str(amount))
        elif isinstance(amount, Decimal):
            self._amount = amount
        else:
            self._amount = Decimal("0")

        # Round to 2 decimal places
        self._amount = self._amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self._currency = currency

    @property
    def amount(self):
        """Get the monetary amount."""
        return self._amount

    @property
    def currency(self):
        """Get the currency code."""
        return self._currency

    def __add__(self, other):
        """Add two money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        """Subtract two money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        """Multiply money by a factor."""
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError("Can only multiply by a number")
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __eq__(self, other):
        """Compare two money objects for equality."""
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency == other.currency
        return False

    def __str__(self):
        """Return string representation of the money value."""
        return f"{self._amount} {self._currency}"

    def __repr__(self):
        """Return string representation for debugging."""
        return f"Money({self._amount}, '{self._currency}')"
