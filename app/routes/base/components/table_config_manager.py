import json
import logging
import traceback
from typing import Dict

logger = logging.getLogger(__name__)


class TableConfigManager:
    """Manages table configuration retrieval and validation."""

    def __init__(self, json_validator):
        self.json_validator = json_validator

    def get_table_config(self, table_name):
        """Retrieve and validate table configuration."""
        try:
            from models.table_config import TableConfig
            table_config = TableConfig.get_config(table_name)
            logger.debug(f"Retrieved table config for {table_name}")

            # Validate table config structure
            if not isinstance(table_config, dict):
                logger.error(f"Table config is not a dictionary: {type(table_config).__name__}")
                table_config = {}

            # Ensure columns exist and are properly formatted
            if 'columns' not in table_config:
                logger.error(f"No 'columns' found in table config for {table_name}")
                table_config['columns'] = []

            # Validate if columns are JSON serializable
            try:
                columns_json = json.dumps(table_config['columns'])
                logger.debug(f"Columns are JSON serializable with {len(table_config.get('columns', []))} columns")
            except TypeError as e:
                logger.error(f"Columns are not JSON serializable: {str(e)}")
                # Fix the columns by ensuring serializability
                table_config['columns'] = self.json_validator.ensure_json_serializable(table_config.get('columns', []))

            # Check for any JSON serialization issues
            issues = self.json_validator.validate_json_serializable(table_config)
            if issues:
                logger.error(f"JSON serialization issues in table_config: {issues}")

            return table_config
        except Exception as e:
            logger.error(f"Error retrieving table config for {table_name}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'columns': []}