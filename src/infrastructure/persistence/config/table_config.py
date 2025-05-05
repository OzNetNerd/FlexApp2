"""
Configuration for database table UI representation.

This module provides functionality to store and retrieve UI configuration
for database tables, such as column visibility and formatting.
"""
import json
from typing import Dict, Optional, Any

from infrastructure.persistence.models.base import BaseModel, db
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class TableConfig(BaseModel):
    """
    Model for storing table UI configuration.

    Attributes:
        id: Primary key.
        table_name: Name of the table this config applies to.
        column_config: JSON string of column configuration.
    """
    table_name = db.Column(db.String(50), unique=True, nullable=False)
    column_config = db.Column(db.Text, nullable=False)

    def __repr__(self) -> str:
        """
        Return string representation of the table config.

        Returns:
            String representation.
        """
        return f"<TableConfig {self.table_name!r}>"

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the column configuration as a dictionary.

        Returns:
            Parsed JSON configuration.
        """
        logger.info(f"Getting configuration for table {self.table_name!r}")
        return json.loads(self.column_config)

    @config.setter
    def config(self, value: Dict[str, Any]) -> None:
        """
        Set the column configuration from a dictionary.

        Args:
            value: Table configuration to store.
        """
        logger.info(f"Setting configuration for table {self.table_name!r}")
        self.column_config = json.dumps(value)

    @classmethod
    def get_config(cls, table_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve configuration for a specific table, handling legacy formats.

        Args:
            table_name: Name of the table.
            default: Optional fallback config.

        Returns:
            Normalized configuration.
        """
        logger.info(f"Fetching configuration for table {table_name!r}")
        config = cls.query.filter_by(table_name=table_name).first()

        if config:
            config_dict = config.config
            if isinstance(config_dict, list):
                logger.info(f"Converting legacy format for table {table_name!r}")
                column_overrides = {col["field"]: {k: v for k, v in col.items() if k != "field"} for col in config_dict
                                    if "field" in col}
                return {
                    "autoGenerateColumns": True,
                    "columnOverrides": column_overrides,
                    "defaultColDef": {
                        "flex": 1,
                        "sortable": True,
                        "filter": True,
                        "resizable": True,
                    },
                    "columns": config_dict,
                }
            return config_dict

        logger.info(f"No configuration found for {table_name!r}, using default.")
        return default or {
            "autoGenerateColumns": True,
            "columnOverrides": {},
            "defaultColDef": {
                "flex": 1,
                "sortable": True,
                "filter": True,
                "resizable": True,
            },
        }

    @classmethod
    def set_config(cls, table_name: str, config_dict: Dict[str, Any]) -> "TableConfig":
        """
        Create or update table configuration.

        Args:
            table_name: Name of the table.
            config_dict: Configuration dictionary.

        Returns:
            The updated or created instance.
        """
        logger.info(f"Setting full configuration for table {table_name!r}")
        config = cls.query.filter_by(table_name=table_name).first() or cls(table_name=table_name)
        config.config = config_dict
        db.session.add(config)
        db.session.commit()
        logger.info(f"Configuration for table {table_name!r} saved.")
        return config

    @classmethod
    def set_column_overrides(cls, table_name: str, column_overrides: Dict[str, Dict[str, Any]]) -> "TableConfig":
        """
        Set overrides for one or more columns in a table.

        Args:
            table_name: Table name.
            column_overrides: Per-field overrides.

        Returns:
            Updated instance.
        """
        logger.info(f"Setting column overrides for table {table_name!r}")
        config = cls.get_config(table_name)
        config["columnOverrides"] = column_overrides
        return cls.set_config(table_name, config)

    @classmethod
    def add_column_override(cls, table_name: str, field_name: str,
                            override_properties: Dict[str, Any]) -> "TableConfig":
        """
        Add or update override settings for a specific column.

        Args:
            table_name: Table name.
            field_name: Column key.
            override_properties: Settings to apply.

        Returns:
            Updated instance.
        """
        logger.info(f"Updating column override for {field_name!r} in table {table_name!r}")
        config = cls.get_config(table_name)
        config.setdefault("columnOverrides", {})[field_name] = override_properties
        return cls.set_config(table_name, config)