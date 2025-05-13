"""
Context classes for SRS templates.

This module defines all the context classes used for rendering SRS templates.
Each context class extends the base WebContext and adds specific attributes
needed for various SRS page templates.
"""

from app.routes.web.utils.context import WebContext


class SRSContext(WebContext):
    """Base context for SRS pages.

    This class serves as the foundation for all SRS-related template contexts.

    Attributes:
        title (str): The page title, defaults to "SRS".
    """

    def __init__(self, title="SRS", **kwargs):
        """Initialize SRS context with a title and additional attributes.

        Args:
            title (str): The page title, defaults to "SRS".
            **kwargs: Additional key-value pairs to add to the context.
        """
        super().__init__(title=title, **kwargs)


class SRSCardListContext(SRSContext):
    """Context for pages displaying card lists.

    This context is used for pages that display lists of flash cards.

    Attributes:
        title (str): The page title.
        cards (list): The list of cards to display.
    """

    def __init__(self, title, cards, **kwargs):
        """Initialize context with title and cards list.

        Args:
            title (str): The page title.
            cards (list): The list of cards to display.
            **kwargs: Additional key-value pairs to add to the context.
        """
        super().__init__(title=title, **kwargs)
        self.cards = cards


class SRSDashboardContext(SRSContext):
    """Context for the SRS dashboard.

    This context contains all the information needed to render the dashboard,
    including statistics, categories, due cards, and progress data.

    Attributes:
        stats (dict): Statistics about the user's SRS usage.
        categories (list): List of card categories with metadata.
        due_cards (list): Cards due for review.
        progress_data (dict): Data for progress charts.
    """

    def __init__(self, stats, categories, due_cards, progress_data, **kwargs):
        """Initialize dashboard context with all required data.

        Args:
            stats (dict): Statistics about the user's SRS usage.
            categories (list): List of card categories with metadata.
            due_cards (list): Cards due for review.
            progress_data (dict): Data for progress charts.
            **kwargs: Additional key-value pairs to add to the context.
        """
        super().__init__(title="SRS Dashboard", **kwargs)
        self.stats = stats
        self.categories = categories
        self.due_cards = due_cards
        self.progress_data = progress_data


class SRSReviewContext(SRSContext):
    """Context for the card review page.

    This context contains all information needed for reviewing a card,
    including navigation information and batch review data.

    Attributes:
        card: The card being reviewed.
        next_item_id: ID of the next card to review, or None.
        prev_item_id: ID of the previous card, or None.
        is_batch (bool): Whether this is part of a batch review.
        remaining_count (int): Number of remaining cards in batch.
    """

    def __init__(self, card, next_item_id, prev_item_id, is_batch, remaining_count):
        """Initialize review context with card and navigation data.

        Args:
            card: The card being reviewed.
            next_item_id: ID of the next card to review, or None.
            prev_item_id: ID of the previous card, or None.
            is_batch (bool): Whether this is part of a batch review.
            remaining_count (int): Number of remaining cards in batch.
        """
        super().__init__(title="Review Card")
        self.card = card
        self.next_item_id = next_item_id
        self.prev_item_id = prev_item_id
        self.is_batch = is_batch
        self.remaining_count = remaining_count


class SRSCategoryContext(SRSContext):
    """Context for the category view page.

    This context contains information about cards in a specific category.

    Attributes:
        cards (list): Cards in the category.
        category_type (str): Type identifier for the category.
        category_name (str): Display name for the category.
        category_color (str): Color associated with the category.
    """

    def __init__(self, cards, category_type, category_name, category_color):
        """Initialize category context with cards and category information.

        Args:
            cards (list): Cards in the category.
            category_type (str): Type identifier for the category.
            category_name (str): Display name for the category.
            category_color (str): Color associated with the category.
        """
        super().__init__(title=f"{category_name} Cards")
        self.cards = cards
        self.category_type = category_type
        self.category_name = category_name
        self.category_color = category_color


class SRSFilteredCardsContext(SRSContext):
    """Context for pages with filtered card lists.

    This context is used for pages that display filtered lists of cards
    based on learning stage, difficulty, or performance.

    Attributes:
        cards (list): The filtered list of cards.
        filters (dict): Applied filters.
        category_counts (dict): Count of cards by category.
        due_category_counts (dict): Count of due cards by category.
        due_today (int): Total number of cards due today.
        total_cards (int): Total number of cards.
        active_tab (str): Currently active tab identifier.
    """

    def __init__(self, cards, title, filters, category_counts, due_category_counts, due_today, total_cards, active_tab):
        """Initialize filtered cards context with cards and filter information.

        Args:
            cards (list): The filtered list of cards.
            title (str): The page title.
            filters (dict): Applied filters.
            category_counts (dict): Count of cards by category.
            due_category_counts (dict): Count of due cards by category.
            due_today (int): Total number of cards due today.
            total_cards (int): Total number of cards.
            active_tab (str): Currently active tab identifier.
        """
        super().__init__(title=title)
        self.cards = cards
        self.filters = filters
        self.category_counts = category_counts
        self.due_category_counts = due_category_counts
        self.due_today = due_today
        self.total_cards = total_cards
        self.active_tab = active_tab


class SRSFilteredContext(SRSContext):
    """Context for the advanced filtered cards page.

    This context extends SRSContext and allows dynamic attribute assignment
    for advanced filtering options.

    Attributes:
        Various attributes are set dynamically based on the kwargs passed in.
    """

    def __init__(self, **kwargs):
        """Initialize filtered context with dynamic attributes.

        Args:
            **kwargs: Key-value pairs to add as attributes to the context.
        """
        super().__init__(title="Filtered Cards", **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class SRSAddCardContext(SRSContext):
    """Context for the add card form.

    This context contains information needed for the add card form,
    including categories and statistics.

    Attributes:
        categories (list): Available categories for the new card.
        stats (dict): SRS statistics.
    """

    def __init__(self, categories, stats):
        """Initialize add card context with categories and stats.

        Args:
            categories (list): Available categories for the new card.
            stats (dict): SRS statistics.
        """
        super().__init__(title="Add New Card")
        self.categories = categories
        self.stats = stats
