"""Category service for managing SRS item categories/decks."""

from typing import Dict, List, Any
from app.models.pages.srs import SRS
from app.models import db
from app.utils.app_logging import get_logger

logger = get_logger()


class SRSCategoryService:
    """Service for managing SRS categories/decks."""

    def __init__(self):
        """Initialize the SRS category service."""
        self.logger = logger
        self.logger.info("SRSCategoryService: Initializing SRS category service")

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all available categories (decks).

        Returns:
            List of category objects with id, name, color, icon, and count
        """
        self.logger.info("SRSCategoryService: Getting all categories")
        # First get all distinct notable_types from the database
        query = db.session.query(SRS.notable_type).distinct()
        db_categories = [row[0] for row in query.all() if row[0]]
        self.logger.info(
            f"SRSCategoryService: Found {len(db_categories)} distinct categories in database: {db_categories}")

        # Get category counts
        category_counts = {}
        for category in db_categories:
            count = SRS.query.filter(SRS.notable_type == category).count()
            category_counts[category] = count

        self.logger.info(f"SRSCategoryService: Category counts: {category_counts}")

        # Merge with predefined categories
        predefined = {
            "company": {"name": "Companies", "color": "primary", "icon": "building"},
            "contact": {"name": "Contacts", "color": "success", "icon": "people"},
            "opportunity": {"name": "Opportunities", "color": "danger", "icon": "graph-up-arrow"},
        }
        self.logger.info(f"SRSCategoryService: Using predefined categories: {list(predefined.keys())}")

        result = []

        # Add predefined categories first
        for category_id, info in predefined.items():
            count = category_counts.get(category_id, 0)
            result.append({
                "id": category_id,
                "name": info["name"],
                "color": info["color"],
                "icon": info["icon"],
                "count": count
            })
            self.logger.info(f"SRSCategoryService: Added predefined category: {category_id} with count {count}")

        # Add custom categories from database that aren't in predefined list
        for category_id in db_categories:
            if category_id not in predefined:
                count = category_counts.get(category_id, 0)
                result.append({
                    "id": category_id,
                    "name": category_id.capitalize(),  # Default name is capitalized ID
                    "color": "secondary",  # Default color
                    "icon": "folder",  # Default icon
                    "count": count,
                })
                self.logger.info(f"SRSCategoryService: Added custom category: {category_id} with count {count}")

        self.logger.info(f"SRSCategoryService: Returning {len(result)} total categories")
        return result

    def create_category(self, name: str, color: str = "secondary", icon: str = "folder") -> Dict[str, Any]:
        """
        Create a new category (deck).

        This doesn't actually create a database record since categories
        are stored as notable_type strings on SRS items. Instead, it
        ensures the category ID is valid and returns a category object.

        Args:
            name: The display name of the category
            color: The color code for the category
            icon: The icon name for the category

        Returns:
            Category object with id, name, color, icon, and count
        """
        self.logger.info(f"SRSCategoryService: Creating category with name '{name}', color '{color}', icon '{icon}'")

        # Normalize the name to create a valid ID
        category_id = name.lower().replace(" ", "_")
        self.logger.info(f"SRSCategoryService: Normalized category ID: {category_id}")

        # Return a category object
        result = {
            "id": category_id,
            "name": name,
            "color": color,
            "icon": icon,
            "count": 0
        }

        self.logger.info(f"SRSCategoryService: Created category object: {result}")
        return result

    def get_category(self, category_id: str) -> Dict[str, Any]:
        """
        Get details for a specific category.

        Args:
            category_id: The ID of the category to retrieve

        Returns:
            Category object with id, name, color, icon, and count

        Raises:
            ValueError: If the category doesn't exist
        """
        self.logger.info(f"SRSCategoryService: Getting details for category '{category_id}'")

        # Check if category exists
        count = SRS.query.filter(SRS.notable_type == category_id).count()
        if count == 0:
            # Check if it's in our predefined list before giving up
            predefined = {
                "company": {"name": "Companies", "color": "primary", "icon": "building"},
                "contact": {"name": "Contacts", "color": "success", "icon": "people"},
                "opportunity": {"name": "Opportunities", "color": "danger", "icon": "graph-up-arrow"},
            }

            if category_id not in predefined:
                self.logger.error(f"SRSCategoryService: Category '{category_id}' not found")
                raise ValueError(f"Category '{category_id}' not found")

        # Get predefined info or use defaults
        predefined = {
            "company": {"name": "Companies", "color": "primary", "icon": "building"},
            "contact": {"name": "Contacts", "color": "success", "icon": "people"},
            "opportunity": {"name": "Opportunities", "color": "danger", "icon": "graph-up-arrow"},
        }

        info = predefined.get(category_id, {
            "name": category_id.capitalize(),
            "color": "secondary",
            "icon": "folder"
        })

        result = {
            "id": category_id,
            "name": info["name"],
            "color": info["color"],
            "icon": info["icon"],
            "count": count
        }

        self.logger.info(f"SRSCategoryService: Returning category details: {result}")
        return result

    def update_category(self, category_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update category metadata.

        Note: This only updates the category definition, it does not rename
        the notable_type in existing items.

        Args:
            category_id: The ID of the category to update
            data: Dictionary with name, color, and/or icon

        Returns:
            Updated category object

        Raises:
            ValueError: If the category doesn't exist
        """
        self.logger.info(f"SRSCategoryService: Updating category '{category_id}' with data: {data}")

        # Verify category exists
        category = self.get_category(category_id)

        # Update fields
        if "name" in data:
            category["name"] = data["name"]

        if "color" in data:
            category["color"] = data["color"]

        if "icon" in data:
            category["icon"] = data["icon"]

        self.logger.info(f"SRSCategoryService: Updated category: {category}")
        return category

    def assign_category(self, srs_item_id: int, category_id: str) -> None:
        """
        Assign a category to an SRS item.

        Args:
            srs_item_id: The ID of the SRS item
            category_id: The category ID to assign

        Raises:
            ValueError: If the SRS item doesn't exist
        """
        self.logger.info(f"SRSCategoryService: Assigning category '{category_id}' to item {srs_item_id}")

        # Get the item
        item = SRS.query.get(srs_item_id)
        if not item:
            self.logger.error(f"SRSCategoryService: SRS item {srs_item_id} not found")
            raise ValueError(f"SRS item {srs_item_id} not found")

        # Update the notable_type
        item.notable_type = category_id
        item.save()

        self.logger.info(f"SRSCategoryService: Successfully assigned category '{category_id}' to item {srs_item_id}")

    def delete_category(self, category_id: str, reassign_to: str = None) -> None:
        """
        Delete a category and optionally reassign its items.

        Args:
            category_id: The ID of the category to delete
            reassign_to: Optional category ID to reassign items to

        Note:
            This doesn't actually delete a database record, it just
            updates the notable_type of all items in the category.
        """
        self.logger.info(f"SRSCategoryService: Deleting category '{category_id}'")

        # Get all items in this category
        items = SRS.query.filter(SRS.notable_type == category_id).all()
        count = len(items)

        self.logger.info(f"SRSCategoryService: Found {count} items in category '{category_id}'")

        if count > 0:
            if reassign_to:
                self.logger.info(f"SRSCategoryService: Reassigning items to category '{reassign_to}'")
                for item in items:
                    item.notable_type = reassign_to
                    item.save()
            else:
                self.logger.info(f"SRSCategoryService: Setting items to NULL category")
                for item in items:
                    item.notable_type = None
                    item.save()

        self.logger.info(f"SRSCategoryService: Successfully deleted category '{category_id}'")

    def get_category_stats(self, category_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific category.

        Args:
            category_id: The ID of the category

        Returns:
            Dictionary with category statistics

        Raises:
            ValueError: If the category doesn't exist
        """
        self.logger.info(f"SRSCategoryService: Getting statistics for category '{category_id}'")

        # Check if category exists
        items = SRS.query.filter(SRS.notable_type == category_id).all()
        if not items:
            self.logger.error(f"SRSCategoryService: Category '{category_id}' not found or empty")
            raise ValueError(f"Category '{category_id}' not found or empty")

        # Basic stats
        total_items = len(items)
        self.logger.info(f"SRSCategoryService: Found {total_items} items in category '{category_id}'")

        # Calculate due items
        from datetime import datetime
        from zoneinfo import ZoneInfo
        due_items = sum(1 for item in items
                        if item.next_review_at and item.next_review_at <= datetime.now(ZoneInfo("UTC")))

        # Calculate new vs reviewed
        new_items = sum(1 for item in items if item.review_count == 0)
        reviewed_items = total_items - new_items

        # Calculate average ease factor
        from app.services.srs.constants import DEFAULT_EASE_FACTOR
        avg_ease = sum(item.ease_factor or DEFAULT_EASE_FACTOR for item in items) / total_items if total_items else 0

        # Calculate mastery
        mastered_items = sum(1 for item in items if item.interval and item.interval > 21)

        stats = {
            "total_items": total_items,
            "due_items": due_items,
            "new_items": new_items,
            "reviewed_items": reviewed_items,
            "mastered_items": mastered_items,
            "avg_ease_factor": round(avg_ease, 2),
            "mastery_percentage": round((mastered_items / total_items) * 100 if total_items else 0, 1)
        }

        self.logger.info(f"SRSCategoryService: Category statistics: {stats}")
        return stats