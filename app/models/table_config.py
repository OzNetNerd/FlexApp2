import json
from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class TableConfig(db.Model, BaseModel):
    __tablename__ = 'table_configs'

    table_name = db.Column(db.String(50), unique=True, nullable=False)
    column_config = db.Column(db.Text, nullable=False)  # JSON string

    def __repr__(self):
        return f'<TableConfig {self.table_name}>'

    @property
    def config(self):
        """Return the column configuration as a Python dictionary."""
        logger.debug(f"Getting configuration for table '{self.table_name}'")
        return json.loads(self.column_config)

    @config.setter
    def config(self, value):
        """Set the column configuration from a Python dictionary."""
        logger.debug(f"Setting configuration for table '{self.table_name}'")
        self.column_config = json.dumps(value)

    @classmethod
    def get_config(cls, table_name, default=None):
        """
        Get configuration for a specific table.

        If the table has an existing configuration in the old format (array of columns),
        it will be converted to the new format with autoGenerateColumns and columnOverrides.
        """
        logger.debug(f"Fetching configuration for table '{table_name}'")
        config = cls.query.filter_by(table_name=table_name).first()
        if config:
            config_dict = config.config

            # Check if this is an old-style config (just an array of column objects)
            if isinstance(config_dict, list):
                logger.debug(f"Converting old configuration format for table '{table_name}'")
                column_overrides = {}
                for column in config_dict:
                    field = column.get('field')
                    if field:
                        # Extract special properties that should be overrides
                        override = {}
                        for key, value in column.items():
                            if key != 'field':
                                override[key] = value
                        if override:
                            column_overrides[field] = override

                # Create new format
                new_config = {'autoGenerateColumns': True, 'columnOverrides': column_overrides, 'defaultColDef': {
                    'flex': 1,
                    'sortable': True,
                    'filter': True,
                    'resizable': True
                }, 'columns': config_dict}

                # Keep original columns for backward compatibility
                return new_config

            # If it's already in the new format, return as is
            return config_dict

        # Return default config if no config exists
        logger.debug(f"No existing configuration found for table '{table_name}', returning default.")
        if default is None:
            default = {
                'autoGenerateColumns': True,
                'columnOverrides': {},
                'defaultColDef': {
                    'flex': 1,
                    'sortable': True,
                    'filter': True,
                    'resizable': True
                }
            }
        return default

    @classmethod
    def set_config(cls, table_name, config_dict):
        """Set configuration for a specific table."""
        logger.debug(f"Setting configuration for table '{table_name}'")
        config = cls.query.filter_by(table_name=table_name).first()
        if not config:
            config = cls(table_name=table_name)

        config.config = config_dict
        db.session.add(config)
        db.session.commit()
        logger.info(f"Configuration for table '{table_name}' set successfully.")
        return config

    @classmethod
    def set_column_overrides(cls, table_name, column_overrides):
        """
        Set only the column overrides for a specific table.
        This preserves other configuration parameters.
        """
        logger.debug(f"Setting column overrides for table '{table_name}'")
        current_config = cls.get_config(table_name)
        current_config['columnOverrides'] = column_overrides
        return cls.set_config(table_name, current_config)

    @classmethod
    def add_column_override(cls, table_name, field_name, override_properties):
        """
        Add or update a single column override.
        """
        logger.debug(f"Adding/updating column override for field '{field_name}' in table '{table_name}'")
        current_config = cls.get_config(table_name)
        if 'columnOverrides' not in current_config:
            current_config['columnOverrides'] = {}

        current_config['columnOverrides'][field_name] = override_properties
        return cls.set_config(table_name, current_config)

    @classmethod
    def set_auto_generate_columns(cls, table_name, auto_generate=True):
        """
        Enable or disable automatic column generation.
        """
        logger.debug(f"Setting autoGenerateColumns for table '{table_name}' to {auto_generate}")
        current_config = cls.get_config(table_name)
        current_config['autoGenerateColumns'] = auto_generate
        return cls.set_config(table_name, current_config)

    @classmethod
    def set_default_col_def(cls, table_name, default_col_def):
        """
        Set the default column definition for a table.
        """
        logger.debug(f"Setting default column definition for table '{table_name}'")
        current_config = cls.get_config(table_name)
        current_config['defaultColDef'] = default_col_def
        return cls.set_config(table_name, current_config)
