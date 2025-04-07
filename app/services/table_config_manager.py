import json
import logging
import traceback
from typing import Dict

logger = logging.getLogger(__name__)


class TableConfigManager:
    """Manages table configuration retrieval and validation."""

    def __init__(self, json_validator):
        """
        Initialize the manager with a JSON validator.

        Args:
            json_validator: Instance of JSONValidator to check data structures.
        """
        self.json_validator = json_validator

    def get_table_config(self, table_name: str) -> Dict:
        """
        Retrieve and validate the table configuration.

        Args:
            table_name (str): The name of the table.

        Returns:
            dict: The validated table configuration.
        """
        try:
            from app.models.table_config import TableConfig

            table_config = TableConfig.get_config(table_name)
            logger.info(f"Retrieved table config for '{table_name}'")
            logger.info(f"Table config: {table_config}")

            if not isinstance(table_config, dict):
                logger.error(f"❌  Table config is not a dictionary: {type(table_config).__name__}")
                table_config = {}

            if "columns" in table_config:
                logger.error(f" 'columns' found: {table_config['columns']}")

            else:
                logger.error(f"❌  No 'columns' found in table")
                table_config["columns"] = []

            try:
                json.dumps(table_config["columns"])
                logger.debug(f"Columns are JSON serializable with {len(table_config.get('columns', []))} columns")
            except TypeError as e:
                logger.error(f"❌  Columns are not JSON serializable: {str(e)}")
                table_config["columns"] = self.json_validator.ensure_json_serializable(table_config.get("columns", []))

            issues = self.json_validator.validate_json_serializable(table_config)
            if issues:
                logger.error(f"❌  JSON serialization issues in table_config: {issues}")

            return table_config
        except Exception as e:
            logger.error(f"❌  Error retrieving table config for {table_name}: {str(e)}")
            logger.error(f"❌  Traceback: {traceback.format_exc()}")
            return {"columns": []}
