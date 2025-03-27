import json
import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class TableConfig(BaseModel):
    """Stores and manages dynamic table configuration for frontend tables.

    Enables AG Grid-compatible column configuration for each table in the CRM.

    Attributes:
        table_name (str): Unique table identifier.
        column_config (str): JSON string of configuration metadata.
    """

    __tablename__ = "table_configs"

    table_name = db.Column(db.String(50), unique=True, nullable=False)
    column_config = db.Column(db.Text, nullable=False)

    def __repr__(self) -> str:
        """Return string representation of the table config.

        Returns:
            str: TableConfig instance name.
        """
        return f"<TableConfig {self.table_name}>"

    @property
    def config(self) -> dict:
        """Get the column configuration as a dictionary.

        Returns:
            dict: Parsed JSON configuration.
        """
        logger.debug(f"Getting configuration for table '{self.table_name}'")
        return json.loads(self.column_config)

    @config.setter
    def config(self, value: dict) -> None:
        """Set the column configuration from a dictionary.

        Args:
            value (dict): Table configuration to store.
        """
        logger.debug(f"Setting configuration for table '{self.table_name}'")
        self.column_config = json.dumps(value)

    @classmethod
    def get_config(cls, table_name: str, default: dict | None = None) -> dict:
        """Retrieve configuration for a specific table, handling legacy formats.

        Args:
            table_name (str): Name of the table.
            default (dict | None): Optional fallback config.

        Returns:
            dict: Normalized configuration.
        """
        logger.debug(f"Fetching configuration for table '{table_name}'")
        config = cls.query.filter_by(table_name=table_name).first()

        if config:
            config_dict = config.config
            if isinstance(config_dict, list):
                logger.debug(f"Converting legacy format for table '{table_name}'")
                column_overrides = {col["field"]: {k: v for k, v in col.items() if k != "field"} for col in config_dict if "field" in col}
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

        logger.debug(f"No configuration found for '{table_name}', using default.")
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
    def set_config(cls, table_name: str, config_dict: dict) -> "TableConfig":
        """Create or update table configuration.

        Args:
            table_name (str): Name of the table.
            config_dict (dict): Configuration dictionary.

        Returns:
            TableConfig: The updated or created instance.
        """
        logger.debug(f"Setting full configuration for table '{table_name}'")
        config = cls.query.filter_by(table_name=table_name).first() or cls(table_name=table_name)
        config.config = config_dict
        db.session.add(config)
        db.session.commit()
        logger.info(f"Configuration for table '{table_name}' saved.")
        return config

    @classmethod
    def set_column_overrides(cls, table_name: str, column_overrides: dict) -> "TableConfig":
        """Set overrides for one or more columns in a table.

        Args:
            table_name (str): Table name.
            column_overrides (dict): Per-field overrides.

        Returns:
            TableConfig: Updated instance.
        """
        logger.debug(f"Setting column overrides for table '{table_name}'")
        config = cls.get_config(table_name)
        config["columnOverrides"] = column_overrides
        return cls.set_config(table_name, config)

    @classmethod
    def add_column_override(cls, table_name: str, field_name: str, override_properties: dict) -> "TableConfig":
        """Add or update override settings for a specific column.

        Args:
            table_name (str): Table name.
            field_name (str): Column key.
            override_properties (dict): Settings to apply.

        Returns:
            TableConfig: Updated instance.
        """
        logger.debug(f"Updating column override for '{field_name}' in table '{table_name}'")
        config = cls.get_config(table_name)
        config.setdefault("columnOverrides", {})[field_name] = override_properties
        return cls.set_config(table_name, config)

    @classmethod
    def set_auto_generate_columns(cls, table_name: str, auto_generate: bool = True) -> "TableConfig":
        """Toggle automatic column generation.

        Args:
            table_name (str): Table name.
            auto_generate (bool): Whether to auto-generate columns.

        Returns:
            TableConfig: Updated instance.
        """
        logger.debug(f"Set autoGenerateColumns to {auto_generate} for '{table_name}'")
        config = cls.get_config(table_name)
        config["autoGenerateColumns"] = auto_generate
        return cls.set_config(table_name, config)

    @classmethod
    def set_default_col_def(cls, table_name: str, default_col_def: dict) -> "TableConfig":
        """Set the default column definition.

        Args:
            table_name (str): Table name.
            default_col_def (dict): Default settings.

        Returns:
            TableConfig: Updated instance.
        """
        logger.debug(f"Updating defaultColDef for table '{table_name}'")
        config = cls.get_config(table_name)
        config["defaultColDef"] = default_col_def
        return cls.set_config(table_name, config)
